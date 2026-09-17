"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


def _utcnow() -> datetime:
    """現在時刻（UTC）を返す.

    Returns:
        タイムゾーン付きの現在時刻
    """
    return datetime.now(timezone.utc)


class ManagedArticle(Base):
    """ローカルで管理する下書き・投稿済み記事を表すモデル."""

    __tablename__ = "managed_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    qiita_id: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(String, nullable=True)
    qiita_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String, default="draft", nullable=False)
    qiita_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )


class StockCache(Base):
    """Qiitaストック一覧のローカルキャッシュ（表示高速化用）を表すモデル."""

    __tablename__ = "stock_cache"

    qiita_item_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    tags: Mapped[str | None] = mapped_column(String, nullable=True)
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
