"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

import respx
from fastapi.testclient import TestClient
from httpx import Response

from src.main import app

client = TestClient(app)


def test_list_stocks_success(qiita_client_override):
    """ストック一覧取得が成功することを確認する."""
    qiita_client_override()
    with respx.mock:
        respx.get("https://qiita.com/api/v2/authenticated_user/stocks").mock(
            return_value=Response(200, json=[{"id": "item1"}])
        )
        response = client.get("/api/stocks")

    assert response.status_code == 200
    assert response.json() == [{"id": "item1"}]


def test_stock_article_success(qiita_client_override):
    """ストック追加が成功することを確認する."""
    qiita_client_override()
    with respx.mock:
        respx.put("https://qiita.com/api/v2/items/item1/stock").mock(return_value=Response(204))
        response = client.put("/api/stocks/item1")

    assert response.status_code == 200
    assert response.json() == {"stocked": True}


def test_unstock_article_success(qiita_client_override):
    """ストック解除が成功することを確認する."""
    qiita_client_override()
    with respx.mock:
        respx.delete("https://qiita.com/api/v2/items/item1/stock").mock(return_value=Response(204))
        response = client.delete("/api/stocks/item1")

    assert response.status_code == 200
    assert response.json() == {"stocked": False}


def test_stock_article_invalid_token_returns_401(qiita_client_override):
    """無効なトークンの場合、ストック追加が401になることを確認する."""
    qiita_client_override("invalid-token")
    with respx.mock:
        respx.put("https://qiita.com/api/v2/items/item1/stock").mock(
            return_value=Response(401, json={"message": "Unauthorized"})
        )
        response = client.put("/api/stocks/item1")

    assert response.status_code == 401
