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


def test_list_articles_success(qiita_client_override):
    """記事一覧取得が成功しQiitaレスポンスをそのまま返すことを確認する."""
    qiita_client_override()
    with respx.mock:
        respx.get("https://qiita.com/api/v2/items").mock(
            return_value=Response(200, json=[{"id": "item1", "title": "テスト記事"}])
        )
        response = client.get("/api/articles", params={"page": 1, "per_page": 10})

    assert response.status_code == 200
    assert response.json() == [{"id": "item1", "title": "テスト記事"}]


def test_get_article_success(qiita_client_override):
    """記事詳細取得が成功することを確認する."""
    qiita_client_override()
    with respx.mock:
        respx.get("https://qiita.com/api/v2/items/item1").mock(
            return_value=Response(200, json={"id": "item1", "title": "テスト記事"})
        )
        response = client.get("/api/articles/item1")

    assert response.status_code == 200
    assert response.json()["id"] == "item1"


def test_get_article_not_found_propagates_error(qiita_client_override):
    """存在しない記事IDの場合、Qiita側の404がそのまま返ることを確認する."""
    qiita_client_override()
    with respx.mock:
        respx.get("https://qiita.com/api/v2/items/unknown").mock(
            return_value=Response(404, json={"message": "Not found"})
        )
        response = client.get("/api/articles/unknown")

    assert response.status_code == 404
