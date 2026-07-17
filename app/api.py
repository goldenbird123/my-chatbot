from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from app.agent import create_agent
from app.config import settings


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_agent():
    """Process singleton; its mutable operations are serialized by Agent itself."""
    return create_agent()


@asynccontextmanager
async def lifespan(app: FastAPI):
    agent = get_agent()
    app.state.agent = agent
    try:
        yield
    finally:
        close = getattr(agent, "close", None)
        if callable(close):
            await run_in_threadpool(close)
        get_agent.cache_clear()


app = FastAPI(
    title="Local AI Assistant",
    version="0.3.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=50_000)

    @field_validator("message")
    @classmethod
    def reject_blank_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message must not be blank")
        return value


class ChatResponse(BaseModel):
    answer: str


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("API request failed: %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "服务内部错误"}},
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": settings.model_name,
        "memory_path": str(settings.memory_path),
        "version": app.version,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    answer = await run_in_threadpool(get_agent().chat, payload.message)
    return ChatResponse(answer=answer)
