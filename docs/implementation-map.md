# Implementation Map

| Path | Purpose |
| --- | --- |
| `app/main.py` | FastAPI application, static file mount, home page route, and router composition. |
| `app/controllers/chat_controller.py` | `GET /api/health` and `POST /api/chat` endpoints. |
| `app/models/schemas.py` | Pydantic request, conversation history, and response schemas. |
| `app/models/assistant.py` | Knowledge loading, lazy embedding model loading, vector caching and ranking, prompt construction, Groq call, and error translation. |
| `web/index.html` | Chat view and Bootstrap-based markup. |
| `web/app.js` | Browser chat state, form submission, loading/error rendering, and API calls. |
| `web/styles.css` | Futuristic visual theme and responsive presentation. |
| `knowledge_base.json` | Library policy corpus used by retrieval. |
| `tests/test_app_integration.py` | API integration coverage with mocked embedding and generation dependencies. |
| `requirements.txt` | Runtime Python dependencies. |
| `requirements-dev.txt` | Development/test dependencies. |
| `Dockerfile` | Container image build and Uvicorn entry point. |
| `.env.example` | Names and safe defaults for local configuration; contains no real secrets. |
| `Copia_de_Hands_On_Pipeline.ipynb` | Educational pipeline reference; not loaded by the web app at runtime. |
| `code/features/20260924-biblioteca-chat-web/` | Archived SDD feature specs, task plan, progress, and implementation notes. |

## Request lifecycle ownership

`web/app.js` calls the chat controller. The controller validates and routes through the schemas, then delegates to `answer_question` in the assistant model. That function loads policies, retrieves semantic matches, calls the provider if context exists, and returns an answer plus source titles. The controller serializes the result as `ChatResponse`.
