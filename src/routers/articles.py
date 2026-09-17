"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.qiita_client import QiitaAPIError, QiitaClient
from src.routers.auth import get_qiita_client

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("")
async def list_articles(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    query: str | None = None,
    tag: str | None = None,
    client: QiitaClient = Depends(get_qiita_client),
) -> list[dict[str, Any]]:
    """記事一覧を取得する（Qiita本体をプロキシ）.

    Args:
        page: ページ番号
        per_page: 1ページあたりの件数（レート制限を意識し既定20・上限100）
        query: 検索クエリ（Qiita検索構文）
        tag: タグで絞り込む場合のタグ名
        client: QiitaClientインスタンス（依存性注入）

    Returns:
        記事情報のリスト

    Raises:
        HTTPException: Qiita API側でエラーが発生した場合
    """
    try:
        return await client.list_items(page=page, per_page=per_page, query=query, tag=tag)
    except QiitaAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/{item_id}")
async def get_article(item_id: str, client: QiitaClient = Depends(get_qiita_client)) -> dict[str, Any]:
    """記事詳細を取得する（Qiita本体をプロキシ）.

    Args:
        item_id: Qiita記事ID
        client: QiitaClientインスタンス（依存性注入）

    Returns:
        記事情報の辞書

    Raises:
        HTTPException: Qiita API側でエラーが発生した場合
    """
    try:
        return await client.get_item(item_id)
    except QiitaAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
