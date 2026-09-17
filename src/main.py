"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from fastapi import FastAPI

from src.routers import auth

app = FastAPI(title="QiitaClientApp")

app.include_router(auth.router)


@app.get("/")
def read_root():
    """ルートエンドポイント。起動確認用のHello World."""
    return {"message": "Hello, QiitaClientApp!"}
