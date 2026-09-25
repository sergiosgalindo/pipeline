# Setup and Deployment

## Requirements

- Python 3.10 or later for the documented local setup.
- A Groq API key for answer generation when a relevant policy is retrieved.
- Disk space and outbound internet access on first use to obtain the default embedding model, unless the model is already cached.
- Docker Engine for container deployment.

The default model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` is public and does not need a Hugging Face token. `HF_TOKEN` is only relevant when switching to a private or gated Hugging Face model.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `GROQ_API_KEY` in `.env`; keep that file private. Then start the server:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --env-file .env
```

Visit `http://127.0.0.1:8000`. Swagger UI is at `/docs`. The app lazily loads embeddings on the first in-scope chat request. To force the Hugging Face client to use an already downloaded cache, set `HF_HOME` to that cache location and `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` in the server environment.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `GROQ_API_KEY` | unset | Server-side credential for Groq. Required for generated answers. |
| `GROQ_MODEL` | `openai/gpt-oss-20b` | Model identifier sent to Groq Chat Completions. |
| `EMBEDDING_MODEL` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Sentence Transformers model name or local path. |
| `EMBEDDING_MIN_SIMILARITY` | `0.4` | Cosine similarity cutoff, inclusive, valid range `-1` to `1`. |
| `HF_TOKEN` | unset | Optional token for gated/private Hugging Face models. Do not expose it to browser code. |
| `HF_HOME` | Hugging Face default; `/model-cache` in Docker | Hugging Face model cache root. |
| `PORT` | `8000` | Port used by the container command. |

## Docker

Build and run from the project root:

```bash
docker build -t library-assistant .
docker run --rm --env-file .env -v library-model-cache:/model-cache -p 8000:8000 library-assistant
```

The image copies application code, web assets, and the policy JSON. `.env` is excluded from the Docker build context; Docker's `--env-file` reads it from the host at container startup. The named volume persists model downloads across container recreations. The first model download requires outbound access from the container.

## Network dependencies

- Browser Bootstrap and font assets load from CDNs.
- Model files may be downloaded from Hugging Face on first use.
- The backend sends generation requests to Groq.

The application can serve its own page without the CDNs, but the page appearance may be degraded if they cannot load. Model caching avoids repeated Hugging Face downloads.
