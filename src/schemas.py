"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

MAX_TAGS = 5


class DraftCreate(BaseModel):
    """下書き新規作成リクエスト."""

    title: str
    body: str | None = None
    tags: list[str] = Field(default_factory=list)
    qiita_private: bool = False

    @field_validator("tags")
    @classmethod
    def validate_tags_count(cls, value: list[str]) -> list[str]:
        """タグ数がQiita仕様の上限（5個）を超えていないか検証する.

        Args:
            value: タグ名のリスト

        Returns:
            検証済みのタグ名リスト

        Raises:
            ValueError: タグ数が5個を超える場合
        """
        if len(value) > MAX_TAGS:
            raise ValueError(f"タグは最大{MAX_TAGS}個までにございます")
        return value


class DraftUpdate(BaseModel):
    """下書き更新リクエスト（全フィールド任意、指定分のみ更新）."""

    title: str | None = None
    body: str | None = None
    tags: list[str] | None = None
    qiita_private: bool | None = None

    @field_validator("tags")
    @classmethod
    def validate_tags_count(cls, value: list[str] | None) -> list[str] | None:
        """タグ数がQiita仕様の上限（5個）を超えていないか検証する.

        Args:
            value: タグ名のリスト（未指定の場合はNone）

        Returns:
            検証済みのタグ名リスト

        Raises:
            ValueError: タグ数が5個を超える場合
        """
        if value is not None and len(value) > MAX_TAGS:
            raise ValueError(f"タグは最大{MAX_TAGS}個までにございます")
        return value


class DraftOut(BaseModel):
    """下書き記事のレスポンス."""

    id: int
    qiita_id: str | None
    title: str
    body: str | None
    tags: list[str]
    qiita_private: bool
    status: str
    qiita_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
