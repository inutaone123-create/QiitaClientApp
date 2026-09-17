"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.qiita_client import QiitaAPIError, QiitaClient
from src.routers.auth import get_qiita_client

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("")
async def list_stocks(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    client: QiitaClient = Depends(get_qiita_client),
) -> list[dict[str, Any]]:
    """自分のストック一覧を取得する.

    Args:
        page: ページ番号
        per_page: 1ページあたりの件数
        client: QiitaClientインスタンス（依存性注入）

    Returns:
        ストックされた記事情報のリスト

    Raises:
        HTTPException: Qiita API側でエラーが発生した場合
    """
    try:
        return await client.list_stocks(page=page, per_page=per_page)
    except QiitaAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.put("/{item_id}")
async def stock_article(
    item_id: str, client: QiitaClient = Depends(get_qiita_client)
) -> dict[str, bool]:
    """記事をストックする.

    Args:
        item_id: Qiita記事ID
        client: QiitaClientインスタンス（依存性注入）

    Returns:
        ストック状態を示す辞書

    Raises:
        HTTPException: Qiita API側でエラーが発生した場合
    """
    try:
        await client.stock_item(item_id)
    except QiitaAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return {"stocked": True}


@router.delete("/{item_id}")
async def unstock_article(
    item_id: str, client: QiitaClient = Depends(get_qiita_client)
) -> dict[str, bool]:
    """記事のストックを解除する.

    Args:
        item_id: Qiita記事ID
        client: QiitaClientインスタンス（依存性注入）

    Returns:
        ストック状態を示す辞書

    Raises:
        HTTPException: Qiita API側でエラーが発生した場合
    """
    try:
        await client.unstock_item(item_id)
    except QiitaAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return {"stocked": False}
