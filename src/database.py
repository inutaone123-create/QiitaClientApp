"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATA_DIR / "qiitaclient.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemyモデルの共通ベースクラス."""


def init_db() -> None:
    """DBを初期化し、未作成のテーブルをすべて作成する."""
    from src import models  # noqa: F401  モデル定義をmetadataへ登録するためのimport

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """リクエストスコープのDBセッションを提供する（FastAPI Depends用）.

    Yields:
        SQLAlchemyセッション
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
