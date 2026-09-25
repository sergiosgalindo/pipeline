# Implementation Map

| Concern | File | Responsibility |
|---|---|---|
| Composition root and view serving | `app/main.py` | Creates FastAPI, mounts `/static`, registers controller and serves `/`. |
| HTTP/API controller | `app/controllers/chat_controller.py` | Implements `/api/chat`, `/api/health`, and maps domain errors to HTTP. |
| Assistant domain/model | `app/models/assistant.py` | Loads policy JSON, retrieves matching fragments, calls Groq, returns answer and sources. |
| API data contracts | `app/models/schemas.py` | Pydantic validation for message, history, request and response. |
| View markup | `web/index.html` | Chat structure, prompt starters, responsive mobile reset control, Bootstrap imports. |
| View styles | `web/styles.css` | Futuristic theme, desktop/mobile layout, focus/typing states. |
| View interaction | `web/app.js` | Submits questions, renders messages and sources, retains page-session history, handles reset. |
| Knowledge source | `knowledge_base.json` | Editable library policy passages. |
| Dependencies | `requirements.txt` | FastAPI and Uvicorn runtime. |
| Container packaging | `Dockerfile`, `.dockerignore` | Builds the web service image without bundling local secrets or development files. |
| Operator instructions | `README.md` | Setup, environment variables, launch command and customization. |

## Local Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY="your_api_key"
uvicorn app.main:app --reload
```

Browse to `http://127.0.0.1:8000`; API docs are at `/docs`.

Container run:

```bash
docker build -t library-assistant .
docker run --rm --env-file .env -p 8000:8000 library-assistant
```
