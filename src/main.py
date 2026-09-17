"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import init_db
from src.routers import auth


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


@app.get("/")
def read_root():
    """ルートエンドポイント。起動確認用のHello World."""
    return {"message": "Hello, QiitaClientApp!"}
