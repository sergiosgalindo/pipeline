"""Punto de entrada FastAPI y ensamblado MVC."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.controllers.chat_controller import router as chat_router


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIEWS_DIR = PROJECT_ROOT / "web"

app = FastAPI(title="Biblioteca · Asistente virtual", version="1.0.0")
app.mount("/static", StaticFiles(directory=VIEWS_DIR), name="static")
app.include_router(chat_router)


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(VIEWS_DIR / "index.html")
