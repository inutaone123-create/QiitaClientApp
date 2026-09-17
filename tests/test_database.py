"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from src.database import DATABASE_PATH, init_db


def test_init_db_creates_sqlite_file():
    """init_db()の実行後にSQLiteファイルが生成されることを確認する."""
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    init_db()

    assert DATABASE_PATH.exists()
