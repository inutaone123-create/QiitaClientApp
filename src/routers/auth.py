"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.qiita_client import QiitaAPIError, QiitaClient

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_qiita_client() -> QiitaClient:
    """QiitaClientの依存性注入用ファクトリ.

    Returns:
        QiitaClientのインスタンス
    """
    return QiitaClient()


@router.get("/verify")
async def verify_token(
    client: QiitaClient = Depends(get_qiita_client),
) -> dict[str, Any]:
    """Qiitaトークンの有効性を確認する.

    Args:
        client: QiitaClientインスタンス（依存性注入）

    Returns:
        認証済みユーザー情報を含む辞書

    Raises:
        HTTPException: トークン未設定・無効時、またはQiita API側でエラーが発生した場合
    """
    try:
        user = await client.get_authenticated_user()
    except QiitaAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return {"authenticated": True, "user": user}
