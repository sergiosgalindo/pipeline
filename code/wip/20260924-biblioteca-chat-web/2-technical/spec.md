# Technical Specification

Status: aligned with the current implementation; runtime verification gaps remain

## Architecture Impact

The application follows MVC within a single FastAPI service:

- **Model:** `app/models/assistant.py` loads the corpus, retrieves fragments, builds context, and calls Groq. `app/models/schemas.py` defines the input/output contracts.
- **Controller:** `app/controllers/chat_controller.py` exposes `/api/chat` and `/api/health`, maps domain errors to HTTP responses, and validates requests with the schemas.
- **View:** `web/index.html`, `web/styles.css`, and `web/app.js` make up the interface. Bootstrap 5.3.3 is loaded from a CDN; custom styles provide the futuristic responsive dark theme.
- **Composition root:** `app/main.py` creates the FastAPI app, registers the router, mounts static assets, and serves the home view.
- **Container packaging:** a root `Dockerfile` builds the FastAPI service image; `.dockerignore` excludes local secrets, virtual environments, Git data, and caches. The image listens on port 8000 and receives `GROQ_API_KEY` at container runtime.

Request flow: browser → `POST /api/chat` → controller → model loads `knowledge_base.json` → embedding-based semantic retrieval → prompt/context/history assembly → Groq Chat Completions API → answer with source labels → message rendered in the browser.

## Relationship to the Pipeline Hands-On

`Copia_de_Hands_On_Pipeline.ipynb` provides the example domain (library policies) and the RAG-plus-Groq-generation pattern. The app is a separate web implementation; it does not run the notebook. The first web version ranked policies by lexical overlap; the current server embeds them with Sentence Transformers. The notebook also trains and saves a LoRA adapter, but the current server neither loads nor uses it: Groq generates the answers. Therefore, the web demo combines knowledge retrieval with remote generation; it must not be described as an integrated RAG + LoRA system.

## Data Model

`knowledge_base.json` is a list of `{ "title": string, "text": string }` objects. The current corpus has 26 policies, one topic each: loans and renewals, late fines, reserve materials, hours, credentials, loan limits, holds, returns, loss or damage, study rooms, carrels, computers and printing, Wi-Fi, noise and food, lockers, electronic resources, interlibrary loan, visitors and minors, photocopying, the catalog, title requests, theses, laptop loans, reference help, accessibility, and conduct. Each entry states the rule and its exceptions so related policies do not contradict one another.

The Pydantic schemas are:

- `ChatMessage`: `role` is limited to `user` or `assistant`; `content` is at most 2000 characters.
- `ChatRequest`: `message` is 1–2000 characters and `history` contains at most 12 messages.
- `ChatResponse`: `answer` and a `sources` list of titles.

## API / Interfaces

### `GET /`

Serves `web/index.html`.

### `GET /static/{asset}`

Serves the view's CSS and JavaScript.

### `GET /api/health`

Returns `{ "ok": true, "configured": boolean }`.

### `POST /api/chat`

Input:

```json
{
  "message": "¿Cuántos días dura el préstamo?",
  "history": []
}
```

Response:

```json
{
  "answer": "El préstamo dura hasta 15 días.",
  "sources": ["Préstamo y renovación"]
}
```

The interface keeps the full conversation in memory and sends only the latest 12 history messages, matching `ChatRequest`. The provider prompt includes at most the latest six of those messages. The provider key is read from `GROQ_API_KEY`; the model is configured with `GROQ_MODEL` and defaults to `openai/gpt-oss-20b`.

## Retrieval and Generation

Retrieval uses a local `SentenceTransformer` model (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` by default) to embed each policy as its title plus text, and to embed each Spanish question. It ranks normalized vectors by cosine similarity, returns up to three results above `EMBEDDING_MIN_SIMILARITY` (default `0.4`), and abstains without calling Groq when none pass the threshold. The model and corpus embeddings are cached in process; changing the corpus invalidates its embedding cache. `EMBEDDING_MODEL` and `EMBEDDING_MIN_SIMILARITY` can be configured through the environment. This follows the reference project's Sentence Transformers embedding approach while using in-process cosine search instead of adding a FAISS dependency for a 26-entry corpus.

With context, the model receives a system message that restricts answers to the policies, up to six prior messages, and the question with retrieved context. The call to Groq's compatible endpoint uses the standard-library `urllib`, temperature `0.2`, a 250-token limit, and a 45-second timeout.

## UI / UX Impact

The view has starter suggestions for loans, fines, reserve materials, hours, study rooms, Wi-Fi, and credentials, plus a message list, a searching state, retrieved sources, readable errors, Enter-to-send, and a new-conversation button. The CSS uses grid, gradient backgrounds, mint accents, and a 720 px media query. On mobile, it hides the sidebar and shows a reset control in the header. Bootstrap and fonts load from CDNs, so the view requires Internet access for those assets.

## Security

- The Groq secret is read from the server process environment.
- The default Hugging Face embedding model is public and needs no token. If an operator selects a private or gated model, `HF_TOKEN` may be supplied through the server environment and must remain server-side.
- The Docker image must not copy `.env` or embed API keys; pass secrets at runtime with Docker's `--env-file` option. Persist the Hugging Face model cache in a named volume to avoid downloading model weights after every container restart.
- Pydantic limits message and history sizes.
- The client uses `textContent` to display answers, preventing generated text from being interpreted as HTML.
- The question and included history are sent to Groq; users should not submit sensitive information.
- Before public deployment, review CORS/origins, rate limiting, privacy/retention, secret management, HTTPS, and content validation.

## Testing Strategy

- Syntax checked with `py_compile` for Python modules and `node --check` for browser JavaScript.
- HTTP integration tests use FastAPI's `TestClient` and replace only the Groq network call with a deterministic fake response. They cover the root page/static assets, health configuration, request validation, retrieval and sources, abstention, and provider timeout mapping.
- Embedding retrieval tests inject deterministic vectors and verify ranking, threshold-based abstention, and context passed to generation without downloading a model or calling a live provider.
- The configured model was evaluated on Spanish paraphrases for loans, late returns, and reserve materials, plus an out-of-corpus question that correctly abstained. Pending: inspect desktop/mobile browser rendering and exercise `/api/chat` with a valid Groq key.

## Risks

- Embedding model downloads require network access on first use unless the model is already cached. The similarity threshold may omit useful context or admit weak matches and must be evaluated against representative questions.
- The app depends on Groq and the availability/capabilities of the configured model.
- The default model name may need updating as Groq availability changes.
- Questions outside the 26 configured policies are rejected. A vague question can retrieve up to three related policies, such as different loan durations, and the answer must follow the policy that names the material.
- A conversation longer than 12 stored messages still sends only the newest 12, so the model does not see the oldest turns.
- The “Online” status indicator is static; the UI does not yet query `/api/health`.
- Bootstrap and CDN fonts may not load offline.
- A container image does not include the Groq key; container runs require a runtime environment file or variable.
- The notebook's trained LoRA adapter is not used for responses. Groq does not load that adapter; integration would require serving a compatible model/adapter from a local runtime or supported inference endpoint.
