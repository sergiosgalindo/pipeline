# Testing, Troubleshooting, and Security

## Integration tests

Install the development dependencies and run:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

The HTTP integration tests use deterministic fakes for embeddings and Groq. They verify routes and the API-to-assistant path without a live provider key or model download. They do not prove that a live Groq account accepts the configured credentials or that external networking is available.

## Troubleshooting

### Chat remains on “Searching policies…”

The browser keeps the pending message while `/api/chat` is unresolved. Check the Uvicorn logs and Network panel for the request duration/status. The first request may load the model and encode the corpus. Later requests reuse in-process model and corpus-vector caches. Provider generation has a 45-second timeout in the current implementation; an error should be returned as HTTP 502. A 403 is a provider rejection, not a RAG retrieval result; inspect its provider error body and verify Groq account/key access and network policy. `GET /api/health` only checks that `GROQ_API_KEY` is present, not that it is valid.

### Embedding model download or load fails

Confirm outbound access to Hugging Face on first use, available disk space, and that `EMBEDDING_MODEL` is spelled correctly. If using offline mode, confirm the model snapshot exists under `HF_HOME`; otherwise the local model load will fail. Use `HF_TOKEN` only for gated/private models that require it.

### Docker cannot access the model or provider

Check that `.env` is supplied at runtime using `--env-file .env`, that the container has outbound network access when needed, and that a writable model cache volume is mounted at `/model-cache`. Do not copy `.env` into the image.

### Page styling or fonts are missing

The page uses CDN-hosted Bootstrap and fonts. Check browser access to the CDN or replace those references with locally hosted assets for an offline deployment.

## Security notes

- Keep `.env` out of Git and container build context. The repository `.gitignore` and `.dockerignore` exclude it.
- Never paste API tokens into source code, documentation, browser JavaScript, screenshots, or issue trackers. If a token is exposed, revoke it and replace it in the local environment.
- `GROQ_API_KEY` and optional `HF_TOKEN` are backend environment variables; the browser never needs them.
- Retrieved knowledge-base passages and user prompts are sent to Groq for generation. Avoid storing sensitive or regulated data in the corpus unless that provider use is approved for the data.
- `configured: true` from the health endpoint is not a credential validity check.

## Current verification status

The project includes an integration suite and the SDD progress log records implementation checks. Live provider access depends on the local Groq account, token, model availability, and network. A provider HTTP 403 must be resolved at that integration boundary; it is not fixed by `HF_TOKEN` because Hugging Face and Groq credentials serve separate services.
