"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import ManagedArticle
from src.qiita_client import QiitaAPIError, QiitaClient
from src.routers.auth import get_qiita_client
from src.schemas import DraftCreate, DraftOut, DraftUpdate

router = APIRouter(prefix="/api/drafts", tags=["drafts"])


def _tags_to_str(tags: list[str]) -> str:
    """タグのリストをDB保存用のカンマ区切り文字列へ変換する.

    Args:
        tags: タグ名のリスト

    Returns:
        カンマ区切りのタグ文字列
    """
    return ",".join(tags)


def _tags_from_str(value: str | None) -> list[str]:
    """DB保存用のカンマ区切り文字列をタグのリストへ変換する.

    Args:
        value: カンマ区切りのタグ文字列（Noneまたは空文字の場合は空リスト）

    Returns:
        タグ名のリスト
    """
    if not value:
        return []
    return value.split(",")


def _to_draft_out(article: ManagedArticle) -> DraftOut:
    """ManagedArticleモデルをDraftOutスキーマへ変換する.

    Args:
        article: 変換対象のManagedArticle

    Returns:
        DraftOutスキーマインスタンス
    """
    return DraftOut(
        id=article.id,
        qiita_id=article.qiita_id,
        title=article.title,
        body=article.body,
        tags=_tags_from_str(article.tags),
        qiita_private=article.qiita_private,
        status=article.status,
        qiita_url=article.qiita_url,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


def _get_draft_or_404(db: Session, draft_id: int) -> ManagedArticle:
    """下書きIDからManagedArticleを取得する。存在しない場合は404を送出する.

    Args:
        db: DBセッション
        draft_id: 下書きID

    Returns:
        該当するManagedArticle

    Raises:
        HTTPException: 該当する下書きが存在しない場合（404）
    """
    article = db.get(ManagedArticle, draft_id)
    if article is None:
        raise HTTPException(status_code=404, detail=f"下書き（id={draft_id}）が見つかりません")
    return article


def _build_qiita_payload(article: ManagedArticle) -> dict[str, Any]:
    """ManagedArticleからQiita API投稿用のペイロードを組み立てる.

    Args:
        article: 変換対象のManagedArticle

    Returns:
        Qiita API（POST/PATCH /items）用のペイロード辞書
    """
    return {
        "title": article.title,
        "body": article.body or "",
        "tags": [{"name": name, "versions": []} for name in _tags_from_str(article.tags)],
        "private": article.qiita_private,
    }


@router.get("")
def list_drafts(db: Session = Depends(get_db)) -> list[DraftOut]:
    """管理記事（下書き）一覧を取得する.

    Args:
        db: DBセッション（依存性注入）

    Returns:
        下書き一覧（更新日時の降順）
    """
    articles = db.query(ManagedArticle).order_by(ManagedArticle.updated_at.desc()).all()
    return [_to_draft_out(a) for a in articles]


@router.post("", status_code=201)
def create_draft(payload: DraftCreate, db: Session = Depends(get_db)) -> DraftOut:
    """新規下書きを作成する.

    Args:
        payload: 下書き作成リクエスト
        db: DBセッション（依存性注入）

    Returns:
        作成された下書き
    """
    article = ManagedArticle(
        title=payload.title,
        body=payload.body,
        tags=_tags_to_str(payload.tags),
        qiita_private=payload.qiita_private,
        status="draft",
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return _to_draft_out(article)


@router.get("/{draft_id}")
def get_draft(draft_id: int, db: Session = Depends(get_db)) -> DraftOut:
    """下書き詳細を取得する.

    Args:
        draft_id: 下書きID
        db: DBセッション（依存性注入）

    Returns:
        下書き詳細
    """
    article = _get_draft_or_404(db, draft_id)
    return _to_draft_out(article)


@router.put("/{draft_id}")
def update_draft(draft_id: int, payload: DraftUpdate, db: Session = Depends(get_db)) -> DraftOut:
    """下書きを編集する（指定されたフィールドのみ更新）.

    Args:
        draft_id: 下書きID
        payload: 更新リクエスト
        db: DBセッション（依存性注入）

    Returns:
        更新後の下書き
    """
    article = _get_draft_or_404(db, draft_id)
    if payload.title is not None:
        article.title = payload.title
    if payload.body is not None:
        article.body = payload.body
    if payload.tags is not None:
        article.tags = _tags_to_str(payload.tags)
    if payload.qiita_private is not None:
        article.qiita_private = payload.qiita_private
    db.commit()
    db.refresh(article)
    return _to_draft_out(article)


@router.delete("/{draft_id}", status_code=204)
def delete_draft(draft_id: int, db: Session = Depends(get_db)) -> None:
    """下書きを削除する.

    Args:
        draft_id: 下書きID
        db: DBセッション（依存性注入）
    """
    article = _get_draft_or_404(db, draft_id)
    db.delete(article)
    db.commit()


@router.post("/{draft_id}/publish")
async def publish_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    client: QiitaClient = Depends(get_qiita_client),
) -> DraftOut:
    """下書きをQiitaへ新規投稿する.

    Args:
        draft_id: 下書きID
        db: DBセッション（依存性注入）
        client: QiitaClientインスタンス（依存性注入）

    Returns:
        投稿後の下書き（qiita_id・qiita_url・statusが更新される）

    Raises:
        HTTPException: 既に投稿済みの場合（409）、またはQiita API側でエラーが発生した場合
    """
    article = _get_draft_or_404(db, draft_id)
    if article.qiita_id is not None:
        raise HTTPException(
            status_code=409,
            detail="この下書きは既にQiitaへ投稿済みです。更新する場合は sync を使用してください",
        )

    try:
        result = await client.create_item(_build_qiita_payload(article))
    except QiitaAPIError as exc:
        article.status = "sync_error"
        db.commit()
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    article.qiita_id = result["id"]
    article.qiita_url = result.get("url")
    article.status = "published"
    db.commit()
    db.refresh(article)
    return _to_draft_out(article)


@router.put("/{draft_id}/sync")
async def sync_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    client: QiitaClient = Depends(get_qiita_client),
) -> DraftOut:
    """Qiita側の記事を、ローカル下書きの内容で更新する.

    Args:
        draft_id: 下書きID
        db: DBセッション（依存性注入）
        client: QiitaClientインスタンス（依存性注入）

    Returns:
        更新後の下書き

    Raises:
        HTTPException: まだQiitaへ投稿されていない場合（400）、またはQiita API側でエラーが発生した場合
    """
    article = _get_draft_or_404(db, draft_id)
    if article.qiita_id is None:
        raise HTTPException(
            status_code=400,
            detail="この下書きはまだQiitaへ投稿されていません。先に publish を実行してください",
        )

    try:
        result = await client.update_item(article.qiita_id, _build_qiita_payload(article))
    except QiitaAPIError as exc:
        article.status = "sync_error"
        db.commit()
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    article.qiita_url = result.get("url")
    article.status = "published"
    db.commit()
    db.refresh(article)
    return _to_draft_out(article)
