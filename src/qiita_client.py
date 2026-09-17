"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

QIITA_API_BASE_URL = "https://qiita.com/api/v2"


class QiitaAPIError(Exception):
    """Qiita API呼び出しで発生したエラーを表す例外."""

    def __init__(self, status_code: int, message: str) -> None:
        """例外を初期化する.

        Args:
            status_code: HTTPステータスコード
            message: エラーメッセージ
        """
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class QiitaAuthError(QiitaAPIError):
    """認証エラー（401 Unauthorized）を表す例外."""


class QiitaTokenNotConfiguredError(QiitaAPIError):
    """QIITA_TOKEN が未設定の場合の例外."""

    def __init__(self) -> None:
        """例外を初期化する."""
        super().__init__(
            status_code=401,
            message="QIITA_TOKEN が設定されていません。.env に有効な個人アクセストークンを設定してください。",
        )


class QiitaClient:
    """Qiita API v2 への認証付きリクエストをラップするクライアント."""

    def __init__(self, token: str | None = None, base_url: str = QIITA_API_BASE_URL) -> None:
        """クライアントを初期化する.

        Args:
            token: Qiita個人アクセストークン。未指定時は環境変数 QIITA_TOKEN を使用する
            base_url: Qiita API のベースURL
        """
        self._token = token if token is not None else os.getenv("QIITA_TOKEN")
        self._base_url = base_url

    def _headers(self) -> dict[str, str]:
        """認証ヘッダーを組み立てる.

        Returns:
            Authorization ヘッダーを含む辞書

        Raises:
            QiitaTokenNotConfiguredError: トークンが未設定の場合
        """
        if not self._token:
            raise QiitaTokenNotConfiguredError()
        return {"Authorization": f"Bearer {self._token}"}

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Qiita APIへHTTPリクエストを送信する.

        429（レート制限）を含め、エラーレスポンスはリトライせずそのまま例外化する。

        Args:
            method: HTTPメソッド
            path: APIパス（例: "/items"）
            **kwargs: httpxへ渡す追加のクエリ・ボディ引数

        Returns:
            httpxのレスポンス

        Raises:
            QiitaAuthError: 401が返却された場合
            QiitaAPIError: 401以外のエラーレスポンスの場合
        """
        headers = self._headers()
        async with httpx.AsyncClient(base_url=self._base_url, timeout=10.0) as client:
            response = await client.request(method, path, headers=headers, **kwargs)

        if response.status_code == 401:
            raise QiitaAuthError(
                status_code=401,
                message="Qiitaトークンが無効です。.env の QIITA_TOKEN を確認してください。",
            )
        if response.status_code >= 400:
            raise QiitaAPIError(
                status_code=response.status_code,
                message=f"Qiita APIエラー（status={response.status_code}）: {response.text}",
            )
        return response

    async def get_authenticated_user(self) -> dict[str, Any]:
        """認証済みユーザー情報を取得する.

        Returns:
            認証ユーザー情報の辞書
        """
        response = await self._request("GET", "/authenticated_user")
        return response.json()

    async def list_items(
        self,
        page: int = 1,
        per_page: int = 20,
        query: str | None = None,
        tag: str | None = None,
    ) -> list[dict[str, Any]]:
        """記事一覧を取得する.

        Args:
            page: ページ番号
            per_page: 1ページあたりの件数
            query: 検索クエリ（Qiita検索構文）
            tag: タグで絞り込む場合のタグ名

        Returns:
            記事情報のリスト
        """
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        query_parts = []
        if query:
            query_parts.append(query)
        if tag:
            query_parts.append(f"tag:{tag}")
        if query_parts:
            params["query"] = " ".join(query_parts)
        response = await self._request("GET", "/items", params=params)
        return response.json()

    async def get_item(self, item_id: str) -> dict[str, Any]:
        """記事詳細を取得する.

        Args:
            item_id: Qiita記事ID

        Returns:
            記事情報の辞書
        """
        response = await self._request("GET", f"/items/{item_id}")
        return response.json()

    async def list_stocks(self, page: int = 1, per_page: int = 20) -> list[dict[str, Any]]:
        """自分のストック一覧を取得する.

        Args:
            page: ページ番号
            per_page: 1ページあたりの件数

        Returns:
            ストックされた記事情報のリスト
        """
        params = {"page": page, "per_page": per_page}
        response = await self._request("GET", "/authenticated_user/stocks", params=params)
        return response.json()

    async def stock_item(self, item_id: str) -> None:
        """記事をストックする.

        Args:
            item_id: Qiita記事ID
        """
        await self._request("PUT", f"/items/{item_id}/stock")

    async def unstock_item(self, item_id: str) -> None:
        """記事のストックを解除する.

        Args:
            item_id: Qiita記事ID
        """
        await self._request("DELETE", f"/items/{item_id}/stock")

    async def create_item(self, payload: dict[str, Any]) -> dict[str, Any]:
        """新規記事をQiitaへ投稿する.

        Args:
            payload: 記事作成パラメータ（title, body, tags, privateなど）

        Returns:
            作成された記事情報
        """
        response = await self._request("POST", "/items", json=payload)
        return response.json()

    async def update_item(self, item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """既存記事を更新する.

        Args:
            item_id: Qiita記事ID
            payload: 更新パラメータ

        Returns:
            更新後の記事情報
        """
        response = await self._request("PATCH", f"/items/{item_id}", json=payload)
        return response.json()
