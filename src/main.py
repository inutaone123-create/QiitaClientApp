"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.database import init_db
from src.routers import articles, auth, drafts, stocks

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーション起動時にDBテーブルを初期化する.

    Args:
        app: FastAPIアプリケーションインスタンス

    Yields:
        None
    """
    init_db()
    yield


app = FastAPI(title="QiitaClientApp", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(stocks.router)
app.include_router(drafts.router)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def read_root() -> FileResponse:
    """ルートエンドポイント。フロントエンド（static/index.html）を返す.

    Returns:
        static/index.html のレスポンス
    """
    return FileResponse(STATIC_DIR / "index.html")
