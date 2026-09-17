"""
QiitaClientApp

This implementation: 2026
License: MIT
"""

import respx
from fastapi.testclient import TestClient
from httpx import Response

from src.main import app

client = TestClient(app)


def test_create_and_get_draft(test_db_session):
    """下書きの新規作成・取得ができることを確認する."""
    create_response = client.post(
        "/api/drafts",
        json={
            "title": "下書きタイトル",
            "body": "本文",
            "tags": ["python", "fastapi"],
            "qiita_private": False,
        },
    )
    assert create_response.status_code == 201
    draft = create_response.json()
    assert draft["title"] == "下書きタイトル"
    assert draft["tags"] == ["python", "fastapi"]
    assert draft["status"] == "draft"
    assert draft["qiita_id"] is None

    get_response = client.get(f"/api/drafts/{draft['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "下書きタイトル"


def test_create_draft_rejects_too_many_tags(test_db_session):
    """タグが6個以上の場合、バリデーションエラー（422）になることを確認する."""
    response = client.post(
        "/api/drafts",
        json={"title": "タイトル", "tags": ["a", "b", "c", "d", "e", "f"]},
    )

    assert response.status_code == 422


def test_list_drafts(test_db_session):
    """下書き一覧が取得できることを確認する."""
    client.post("/api/drafts", json={"title": "記事1", "tags": []})
    client.post("/api/drafts", json={"title": "記事2", "tags": []})

    response = client.get("/api/drafts")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_draft(test_db_session):
    """下書きの編集ができることを確認する."""
    created = client.post(
        "/api/drafts", json={"title": "旧タイトル", "tags": []}
    ).json()

    response = client.put(f"/api/drafts/{created['id']}", json={"title": "新タイトル"})

    assert response.status_code == 200
    assert response.json()["title"] == "新タイトル"


def test_delete_draft(test_db_session):
    """下書きの削除ができることを確認する."""
    created = client.post("/api/drafts", json={"title": "削除対象", "tags": []}).json()

    delete_response = client.delete(f"/api/drafts/{created['id']}")
    get_response = client.get(f"/api/drafts/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_get_draft_not_found(test_db_session):
    """存在しない下書きIDの取得が404になることを確認する."""
    response = client.get("/api/drafts/9999")

    assert response.status_code == 404


def test_publish_draft_success(test_db_session, qiita_client_override):
    """下書きをQiitaへ新規投稿し、qiita_id・statusが更新されることを確認する."""
    qiita_client_override()
    created = client.post(
        "/api/drafts", json={"title": "投稿予定", "body": "本文", "tags": ["python"]}
    ).json()

    with respx.mock:
        respx.post("https://qiita.com/api/v2/items").mock(
            return_value=Response(
                201,
                json={
                    "id": "new_item_id",
                    "url": "https://qiita.com/user/items/new_item_id",
                },
            )
        )
        response = client.post(f"/api/drafts/{created['id']}/publish")

    assert response.status_code == 200
    body = response.json()
    assert body["qiita_id"] == "new_item_id"
    assert body["status"] == "published"
    assert body["qiita_url"] == "https://qiita.com/user/items/new_item_id"


def test_publish_draft_already_published_returns_409(
    test_db_session, qiita_client_override
):
    """既に投稿済みの下書きを再度publishすると409になることを確認する."""
    qiita_client_override()
    created = client.post("/api/drafts", json={"title": "投稿予定", "tags": []}).json()

    with respx.mock:
        respx.post("https://qiita.com/api/v2/items").mock(
            return_value=Response(
                201, json={"id": "item_x", "url": "https://qiita.com/user/items/item_x"}
            )
        )
        client.post(f"/api/drafts/{created['id']}/publish")
        response = client.post(f"/api/drafts/{created['id']}/publish")

    assert response.status_code == 409


def test_sync_draft_requires_publish_first(test_db_session, qiita_client_override):
    """未投稿の下書きをsyncしようとすると400になることを確認する."""
    qiita_client_override()
    created = client.post("/api/drafts", json={"title": "未投稿", "tags": []}).json()

    response = client.put(f"/api/drafts/{created['id']}/sync")

    assert response.status_code == 400


def test_sync_draft_success(test_db_session, qiita_client_override):
    """投稿済みの下書きをsyncするとQiita側が更新されることを確認する."""
    qiita_client_override()
    created = client.post(
        "/api/drafts", json={"title": "元タイトル", "tags": []}
    ).json()

    with respx.mock:
        respx.post("https://qiita.com/api/v2/items").mock(
            return_value=Response(
                201, json={"id": "item_y", "url": "https://qiita.com/user/items/item_y"}
            )
        )
        client.post(f"/api/drafts/{created['id']}/publish")

    client.put(f"/api/drafts/{created['id']}", json={"title": "更新後タイトル"})

    with respx.mock:
        respx.patch("https://qiita.com/api/v2/items/item_y").mock(
            return_value=Response(
                200, json={"id": "item_y", "url": "https://qiita.com/user/items/item_y"}
            )
        )
        response = client.put(f"/api/drafts/{created['id']}/sync")

    assert response.status_code == 200
    assert response.json()["status"] == "published"


def test_publish_draft_qiita_error_sets_sync_error_status(
    test_db_session, qiita_client_override
):
    """Qiita API側でエラーが発生した場合、statusがsync_errorになることを確認する."""
    qiita_client_override()
    created = client.post("/api/drafts", json={"title": "投稿予定", "tags": []}).json()

    with respx.mock:
        respx.post("https://qiita.com/api/v2/items").mock(
            return_value=Response(401, json={"message": "Unauthorized"})
        )
        response = client.post(f"/api/drafts/{created['id']}/publish")

    assert response.status_code == 401

    get_response = client.get(f"/api/drafts/{created['id']}")
    assert get_response.json()["status"] == "sync_error"
