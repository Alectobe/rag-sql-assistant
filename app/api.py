"""FastAPI surface: POST /ask -> {answer, sql, rows, error}."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from app.pipeline import ask

app = FastAPI(title="RAG SQL Assistant", version="0.1.0")


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask")
def ask_endpoint(req: AskRequest) -> dict:
    return ask(req.question).to_dict()
