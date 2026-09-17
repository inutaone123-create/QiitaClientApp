"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from collections.abc import Callable, Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app
from src.qiita_client import QiitaClient
from src.routers.auth import get_qiita_client


@pytest.fixture
def test_db_session() -> Generator[sessionmaker, None, None]:
    """テスト用インメモリDBセッションをFastAPIの依存性として差し込む.

    Yields:
        テスト用セッションのファクトリ（sessionmaker）
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(bind=engine)

    def _override_get_db() -> Generator[Session, None, None]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield testing_session_local
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def qiita_client_override() -> Generator[Callable[[str], None], None, None]:
    """QiitaClientを任意のテスト用トークンに差し替えるヘルパーを提供する.

    Yields:
        呼び出すとQiitaClientの依存性をトークン付きで差し替える関数
    """

    def _apply(token: str = "valid-token") -> None:
        app.dependency_overrides[get_qiita_client] = lambda: QiitaClient(token=token)

    yield _apply
    app.dependency_overrides.pop(get_qiita_client, None)
