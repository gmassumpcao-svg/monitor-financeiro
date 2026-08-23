"""Monitor Financeiro — API and UI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import agent, db
from . import summary as summary_mod

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

app = FastAPI(title="Monitor Financeiro", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


class ChatIn(BaseModel):
    message: str = Field(..., min_length=0, max_length=4000)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/profile")
def profile() -> dict[str, Any]:
    return db.get_profile()


@app.get("/api/summary")
def get_summary(ano: Optional[int] = None, mes: Optional[int] = None) -> dict[str, Any]:
    return summary_mod.summarize(ano, mes)


@app.get("/api/lancamentos")
def get_lancamentos(ano: Optional[int] = None, mes: Optional[int] = None) -> list[dict[str, Any]]:
    return db.list_lancamentos(ano, mes)


@app.get("/api/trabalhos")
def get_trabalhos() -> dict[str, Any]:
    return summary_mod.trabalhos_view()


@app.get("/api/gastos")
def get_gastos(meses: int = 6) -> dict[str, Any]:
    return summary_mod.gastos_por_periodo(max(1, min(meses, 24)))


@app.get("/api/pending")
def get_pending() -> dict[str, Any]:
    return {"pending": db.get_pending()}


@app.post("/api/chat")
def chat(body: ChatIn) -> dict[str, Any]:
    return agent.handle(body.message)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
