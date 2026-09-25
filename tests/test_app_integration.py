"""HTTP integration tests for the FastAPI application and assistant pipeline."""

import json
import subprocess
from pathlib import Path
from typing import Any, Iterator

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.models import assistant


class FakeEmbeddingModel:
    """Deterministic vectors for exercising semantic ranking without downloads."""

    def encode(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        policy_axes = _policy_axes()
        vectors = []
        for text in texts:
            policy_text = text.split("\n", 1)[-1]
            if policy_text in policy_axes:
                vectors.append(_axis(policy_axes[policy_text]))
            elif "semanas" in text or "quedarme con un libro" in text or "préstamo" in text:
                vector = _axis(0)
                vector[0] = 0.98
                vector[1] = 0.1
                vectors.append(vector)
            else:
                vectors.append(_axis(31))
        return vectors


def _axis(index: int, size: int = 32) -> list[float]:
    vector = [0.0] * size
    vector[index] = 1.0
    return vector


def _policy_axes() -> dict[str, int]:
    """Keep the original three policies on fixed axes and isolate every added policy."""
    axes: dict[str, int] = {}
    next_axis = 3
    for document in assistant.load_knowledge():
        text = document["text"]
        if text.startswith("Los libros se prestan"):
            axes[text] = 0
        elif text.startswith("Las devoluciones tardías"):
            axes[text] = 1
        elif text.startswith("Los libros de la sección de reserva"):
            axes[text] = 2
        else:
            axes[text] = next_axis
            next_axis += 1
    return axes


@pytest.fixture
def fake_embeddings(monkeypatch: Any) -> Iterator[None]:
    monkeypatch.setattr(assistant, "get_embedding_model", lambda: FakeEmbeddingModel())
    monkeypatch.setenv("EMBEDDING_MIN_SIMILARITY", "0.4")
    assistant.clear_embedding_cache()
    yield
    assistant.clear_embedding_cache()


class FakeGroqResponse:
    def __init__(self, content: str) -> None:
        self.content = content

    def __enter__(self) -> "FakeGroqResponse":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps({
            "choices": [{"message": {"content": self.content}}]
        }).encode("utf-8")


def test_web_entry_and_static_assets_are_served() -> None:
    with TestClient(app) as client:
        page = client.get("/")
        script = client.get("/static/app.js")
        styles = client.get("/static/styles.css")

    assert page.status_code == 200
    assert "text/html" in page.headers["content-type"]
    assert "/static/app.js" in page.text
    assert script.status_code == 200
    assert "fetch('/api/chat'" in script.text
    assert styles.status_code == 200


def test_chat_runs_embedding_retrieval_generation_and_returns_source(
    monkeypatch: Any, fake_embeddings: None
) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "integration-test-key")
    calls = []

    def fake_urlopen(request: Any, timeout: int) -> FakeGroqResponse:
        calls.append((request, timeout))
        return FakeGroqResponse("El préstamo dura hasta 15 días.")

    monkeypatch.setattr(assistant.urllib.request, "urlopen", fake_urlopen)

    with TestClient(app) as client:
        response = client.post("/api/chat", json={
            "message": "¿Por cuántas semanas puedo quedarme con un libro?",
            "history": [],
        })

    assert response.status_code == 200
    assert response.json() == {
        "answer": "El préstamo dura hasta 15 días.",
        "sources": ["Préstamo y renovación"],
    }
    assert len(calls) == 1
    request, timeout = calls[0]
    assert request.get_header("Authorization") == "Bearer integration-test-key"
    assert timeout == 45
    sent_payload = json.loads(request.data.decode("utf-8"))
    assert sent_payload["messages"][-1]["content"].find("15 días") >= 0


def test_out_of_scope_question_abstains_without_calling_groq(
    monkeypatch: Any, fake_embeddings: None
) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "integration-test-key")

    def unexpected_urlopen(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("Groq must not be called when retrieval finds no context")

    monkeypatch.setattr(assistant.urllib.request, "urlopen", unexpected_urlopen)

    with TestClient(app) as client:
        response = client.post("/api/chat", json={
            "message": "¿Cuál es el clima en Marte?",
            "history": [],
        })

    assert response.status_code == 200
    assert response.json()["sources"] == []
    assert "No encuentro información" in response.json()["answer"]


def test_chat_validation_and_provider_failure_are_reported(
    monkeypatch: Any, fake_embeddings: None
) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "integration-test-key")

    with TestClient(app) as client:
        invalid = client.post("/api/chat", json={"message": "", "history": []})
        monkeypatch.setattr(
            assistant.urllib.request,
            "urlopen",
            lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError()),
        )
        provider_error = client.post("/api/chat", json={
            "message": "¿Cuántos días dura el préstamo?",
            "history": [],
        })

    assert invalid.status_code == 422
    assert provider_error.status_code == 502
    assert "conectar con Groq" in provider_error.json()["detail"]


def test_browser_submits_only_the_newest_twelve_history_messages() -> None:
    """Seven completed exchanges store 14 messages; the next request must keep the newest 12."""
    script = r"""
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync('web/app.js', 'utf8');
const sandbox = {};
vm.runInNewContext(code, sandbox);
const items = [];
for (let exchange = 1; exchange <= 7; exchange += 1) {
  items.push({ role: 'user', content: `q${exchange}` });
  items.push({ role: 'assistant', content: `a${exchange}` });
}
const sent = sandbox.submittedHistory(items);
if (sent.length !== 12) throw new Error(`expected 12 messages, got ${sent.length}`);
if (sent[0].content !== 'q2' || sent[sent.length - 1].content !== 'a7') {
  throw new Error(`newest context was not retained: ${sent.map((item) => item.content).join(',')}`);
}
if (items[0].content !== 'q1' || items.length !== 14) {
  throw new Error('capping the request must not drop messages from the local conversation');
}
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_api_accepts_twelve_history_messages_and_rejects_thirteen(
    monkeypatch: Any, fake_embeddings: None
) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "integration-test-key")
    monkeypatch.setattr(
        assistant.urllib.request,
        "urlopen",
        lambda *args, **kwargs: FakeGroqResponse("El préstamo dura hasta 15 días."),
    )
    accepted_history = [
        {"role": "user" if index % 2 == 0 else "assistant", "content": f"m{index}"}
        for index in range(12)
    ]

    with TestClient(app) as client:
        accepted = client.post("/api/chat", json={
            "message": "¿Cuántos días dura el préstamo?",
            "history": accepted_history,
        })
        rejected = client.post("/api/chat", json={
            "message": "¿Cuántos días dura el préstamo?",
            "history": accepted_history + [{"role": "user", "content": "m12"}],
        })

    assert accepted.status_code == 200
    assert rejected.status_code == 422


def test_health_reports_provider_configuration(monkeypatch: Any) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True, "configured": False}


def test_embedding_search_ranks_paraphrase_and_applies_threshold(
    fake_embeddings: None,
) -> None:
    documents = assistant.load_knowledge()

    paraphrase_results = assistant.retrieve(
        "¿Por cuántas semanas puedo quedarme con un libro?", documents
    )
    unrelated_results = assistant.retrieve("¿Cuál es el clima en Marte?", documents)

    assert paraphrase_results[0]["title"] == "Préstamo y renovación"
    assert unrelated_results == []
