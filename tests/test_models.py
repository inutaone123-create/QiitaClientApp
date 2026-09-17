"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.database import Base
from src.models import ManagedArticle, StockCache


def _make_session() -> Session:
    """テスト用のインメモリSQLiteセッションを生成する.

    Returns:
        テーブル作成済みのSQLAlchemyセッション
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_managed_article_defaults_and_persistence():
    """ManagedArticleがデフォルト値付きで作成・取得できることを確認する."""
    session = _make_session()
    article = ManagedArticle(title="テスト記事", body="本文", tags="python,fastapi")
    session.add(article)
    session.commit()

    saved = session.query(ManagedArticle).first()

    assert saved is not None
    assert saved.title == "テスト記事"
    assert saved.qiita_id is None
    assert saved.qiita_private is False
    assert saved.status == "draft"
    assert saved.created_at is not None
    assert saved.updated_at is not None


def test_stock_cache_persistence():
    """StockCacheが主キー（qiita_item_id）で作成・取得できることを確認する."""
    session = _make_session()
    stock = StockCache(
        qiita_item_id="item123",
        title="キャッシュ記事",
        url="https://qiita.com/user/items/item123",
        tags="python",
    )
    session.add(stock)
    session.commit()

    saved = session.get(StockCache, "item123")

    assert saved is not None
    assert saved.title == "キャッシュ記事"
    assert saved.cached_at is not None
