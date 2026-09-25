# Library Assistant

A responsive web chat built with **FastAPI**, **Bootstrap 5**, and an **MVC** structure. It retrieves library policies from `knowledge_base.json` and generates concise answers with Groq. If the available knowledge base does not cover a question, the assistant says so.

## MVC Structure

- `app/models/`: message schemas and assistant logic (RAG retrieval and response generation).
- `app/controllers/`: chat and health routes.
- `web/`: HTML view, styles, and chat interactions. Bootstrap provides the component foundation; `styles.css` adds the futuristic theme and responsive layout.
- `knowledge_base.json`: editable policies used by retrieval.

## Run Locally

Requires Python 3.10 or later and a Groq API key. Sentence Transformers downloads the configured embedding model on first use if it is not already cached; allow enough disk space and an Internet connection.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GROQ_API_KEY to your key.
uvicorn app.main:app --reload --env-file .env
```

Open `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

In Windows PowerShell, copy `.env.example` to `.env`, set `GROQ_API_KEY` in that file, then start Uvicorn with `--env-file .env`. The local `.env` file is ignored by Git; do not commit it.

## Run with Docker

Create `.env` as described above, then build and run the container:

```bash
docker build -t library-assistant .
docker run --rm --env-file .env -v library-model-cache:/model-cache -p 8000:8000 library-assistant
```

Open `http://localhost:8000`. `.env` is excluded from the image build context, while `--env-file .env` reads it from the host and supplies its variables to the container at runtime. The named volume keeps downloaded embedding model files across container restarts. The first request downloads the model and requires outbound Internet access. The container listens on port 8000 and can be configured with `PORT` if needed.

## Customize

Edit `knowledge_base.json` to add policies. Each entry must have `title` and `text` fields. Set `GROQ_MODEL` to choose another model compatible with Groq's endpoint; the default is the model used in the Pipeline notebook. Set `EMBEDDING_MODEL` to choose a Sentence Transformers model and `EMBEDDING_MIN_SIMILARITY` (from `-1` to `1`) to adjust the cosine-similarity cutoff. The default multilingual model is `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; it is public and does not require an HF token, but its weights must be downloaded on first use. Set `HF_TOKEN` only if you configure a private or gated model. Policy embeddings are cached in memory and rebuilt when the corpus text changes.

The web interface loads Bootstrap and fonts from CDNs, so those assets require an Internet connection. The backend calls Groq; the API key is never sent to the browser.

## Run Integration Tests

Install the development dependencies and run the HTTP integration suite:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The tests exercise the web routes and complete API-to-assistant flow. Embeddings and Groq are replaced with deterministic fakes so the suite does not download a model, require a live API key, or make external provider calls.

The current web app combines policy retrieval with Groq generation. It does not load the LoRA adapter trained in the notebook; the notebook is reference material and the app is a separate web implementation.

## SDD Specifications

The implementation is documented in [code/wip/20260924-biblioteca-chat-web](code/wip/20260924-biblioteca-chat-web/): functional and technical specifications, task plan, implementation progress, and file map. The HTTP integration suite passes; live provider response and browser rendering checks remain pending.

## Project Documentation

See [`docs/`](docs/) for the architecture and sequence/flow diagrams, API reference and OpenAPI specification, setup and deployment instructions, RAG/knowledge-base details, troubleshooting guidance, and implementation map.
