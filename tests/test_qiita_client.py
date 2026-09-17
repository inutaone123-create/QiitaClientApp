"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

import pytest
import respx
from httpx import Response

from src.qiita_client import (
    QiitaAPIError,
    QiitaAuthError,
    QiitaClient,
    QiitaTokenNotConfiguredError,
)


@respx.mock
async def test_get_authenticated_user_success():
    """有効なトークンで認証ユーザー情報が取得できることを確認する."""
    respx.get("https://qiita.com/api/v2/authenticated_user").mock(
        return_value=Response(200, json={"id": "test_user"})
    )
    client = QiitaClient(token="valid-token")

    user = await client.get_authenticated_user()

    assert user == {"id": "test_user"}


@respx.mock
async def test_get_authenticated_user_invalid_token_raises_auth_error():
    """無効なトークンでQiitaAuthErrorが送出されることを確認する."""
    respx.get("https://qiita.com/api/v2/authenticated_user").mock(
        return_value=Response(401, json={"message": "Unauthorized"})
    )
    client = QiitaClient(token="invalid-token")

    with pytest.raises(QiitaAuthError) as exc_info:
        await client.get_authenticated_user()

    assert exc_info.value.status_code == 401


async def test_no_token_raises_token_not_configured_error():
    """トークン未設定時にQiitaTokenNotConfiguredErrorが送出されることを確認する."""
    client = QiitaClient(token="")

    with pytest.raises(QiitaTokenNotConfiguredError):
        await client.get_authenticated_user()


@respx.mock
async def test_rate_limit_error_is_not_retried():
    """429（レート制限）時はリトライせずQiitaAPIErrorがそのまま送出されることを確認する."""
    route = respx.get("https://qiita.com/api/v2/items").mock(
        return_value=Response(429, json={"message": "Too Many Requests"})
    )
    client = QiitaClient(token="valid-token")

    with pytest.raises(QiitaAPIError) as exc_info:
        await client.list_items()

    assert exc_info.value.status_code == 429
    assert route.call_count == 1


@respx.mock
async def test_list_items_builds_query_from_query_and_tag():
    """query・tagの両方指定時に検索クエリが正しく組み立てられることを確認する."""
    route = respx.get("https://qiita.com/api/v2/items").mock(
        return_value=Response(200, json=[])
    )
    client = QiitaClient(token="valid-token")

    await client.list_items(page=2, per_page=10, query="FastAPI", tag="python")

    request = route.calls.last.request
    assert request.url.params["page"] == "2"
    assert request.url.params["per_page"] == "10"
    assert request.url.params["query"] == "FastAPI tag:python"


@respx.mock
async def test_stock_item_and_unstock_item():
    """ストック追加・解除がエラーなく完了することを確認する."""
    respx.put("https://qiita.com/api/v2/items/item123/stock").mock(return_value=Response(204))
    respx.delete("https://qiita.com/api/v2/items/item123/stock").mock(return_value=Response(204))
    client = QiitaClient(token="valid-token")

    await client.stock_item("item123")
    await client.unstock_item("item123")


@respx.mock
async def test_create_item_and_update_item():
    """記事の新規作成・更新がQiita APIへ正しくリクエストされることを確認する."""
    respx.post("https://qiita.com/api/v2/items").mock(
        return_value=Response(201, json={"id": "new_item", "title": "タイトル"})
    )
    respx.patch("https://qiita.com/api/v2/items/new_item").mock(
        return_value=Response(200, json={"id": "new_item", "title": "更新後タイトル"})
    )
    client = QiitaClient(token="valid-token")

    created = await client.create_item({"title": "タイトル", "body": "本文", "tags": []})
    updated = await client.update_item("new_item", {"title": "更新後タイトル"})

    assert created["id"] == "new_item"
    assert updated["title"] == "更新後タイトル"
