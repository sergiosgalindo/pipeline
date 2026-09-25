# Implementation Summary

Status: archived after verification

## Implemented Behavior

The library web assistant answers Spanish policy questions from `knowledge_base.json` (27 policies). A visitor opens a Bootstrap chat, sends a question with Enter, the send button, or a suggestion card, and sees the answer plus the titles of the retrieved policies. The conversation stays in the browser session and can be reset. On viewports below 720 px the sidebar is hidden and the header shows the reset control.

`POST /api/chat` embeds the question and each policy title plus text with `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, ranks them by cosine similarity, and keeps up to three policies at or above `EMBEDDING_MIN_SIMILARITY` (default `0.4`). Below that threshold the API abstains in Spanish and does not call Groq. With context, Groq Chat Completions receives a policy-only system prompt, at most the last six history messages, temperature `0.2`, `max_completion_tokens` 512, `reasoning_effort` `low`, and `User-Agent: library-assistant/1.0`. The browser sends at most the newest 12 history messages. `GET /api/health` reports whether `GROQ_API_KEY` is configured. The key stays on the server.

The service runs with Uvicorn and as the `library-assistant` image. The image copies the app, web assets, and policy JSON. `.env` is supplied at runtime.

## Changed Files

- `app/main.py`, `app/controllers/chat_controller.py`, `app/models/assistant.py`, `app/models/schemas.py`: FastAPI MVC, retrieval, Groq call, and request limits.
- `web/index.html`, `web/styles.css`, `web/app.js`: Spanish chat, suggestions, sources, history cap, and desktop/mobile layout.
- `knowledge_base.json`: 27 Spanish library policies.
- `requirements.txt`, `requirements-dev.txt`, `tests/test_app_integration.py`: runtime dependencies and HTTP/RAG tests with fake embeddings and a fake Groq response.
- `Dockerfile`, `.dockerignore`: image build that excludes secrets and the local model cache.
- `README.md`, `CHANGELOG.md`, `docs/`: English setup, architecture, and the rendered documentation page.
- This feature package: functional spec, technical spec, task plan, progress, layout screenshots, and this summary.

## Tests and Checks

- `.venv/bin/python -m pytest -q` — 8 passed (page and static assets, health, validation, retrieval and sources, abstention, provider timeout, and the 12-message history cap).
- `py_compile` on the application modules and `node --check web/app.js` — passed earlier in this feature.
- Live checks: `/` and `/api/health` returned 200; `/api/chat` returned a sourced Spanish answer, including a container request on host port 8002 after the embedding weights were present in the model volume.
- Desktop 1280×800 and mobile 390×844 layout checks passed. Evidence is in `4-implementation/artifacts/`.

## Known Limitations

- The image does not contain the embedding weights (about 450 MB). A new container downloads them on the first in-scope question unless a cache is already mounted at `/model-cache`. That download can stall; an empty volume mounted on `/model-cache` also hides any weights later baked at that same path.
- Answers require Groq. Bootstrap and fonts load from CDNs.
- The “Online” indicator does not call `/api/health`.
- Only the newest 12 history messages are sent, and retrieval can miss or loosely match a question depending on the similarity threshold.
- Authentication, persistent chats, administration, orchestration, and the notebook LoRA adapter are out of scope.
