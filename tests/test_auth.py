"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

import respx
from fastapi.testclient import TestClient
from httpx import Response

from src.main import app
from src.qiita_client import QiitaClient
from src.routers.auth import get_qiita_client

client = TestClient(app)


def test_verify_success():
    """有効なトークンで /api/auth/verify が認証ユーザー情報を返すことを確認する."""
    app.dependency_overrides[get_qiita_client] = lambda: QiitaClient(
        token="valid-token"
    )
    try:
        with respx.mock:
            respx.get("https://qiita.com/api/v2/authenticated_user").mock(
                return_value=Response(200, json={"id": "test_user"})
            )
            response = client.get("/api/auth/verify")

        assert response.status_code == 200
        assert response.json() == {"authenticated": True, "user": {"id": "test_user"}}
    finally:
        app.dependency_overrides.clear()


def test_verify_invalid_token_returns_401():
    """無効なトークンで /api/auth/verify が401を返すことを確認する."""
    app.dependency_overrides[get_qiita_client] = lambda: QiitaClient(
        token="invalid-token"
    )
    try:
        with respx.mock:
            respx.get("https://qiita.com/api/v2/authenticated_user").mock(
                return_value=Response(401, json={"message": "Unauthorized"})
            )
            response = client.get("/api/auth/verify")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_verify_no_token_returns_401():
    """トークン未設定で /api/auth/verify が401を返すことを確認する."""
    app.dependency_overrides[get_qiita_client] = lambda: QiitaClient(token="")
    try:
        response = client.get("/api/auth/verify")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
