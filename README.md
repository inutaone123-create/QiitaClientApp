# QiitaClientApp

Qiita API v2 を利用した非公式クライアントアプリ（個人開発・記事ネタ用）。

ストア公開は行わず、ローカルWebアプリ + GitHubリポジトリで完結させることを方針とする。

## できること

- 記事の一覧取得・検索（キーワード・タグ）・詳細閲覧
- ストックの一覧・追加・解除
- ローカルで下書きを編集し、Qiitaへ新規投稿・更新（下書き一覧・Markdownプレビュー付きエディタ）

## APIエンドポイント

```
GET    /api/auth/verify              認証（トークン）確認

GET    /api/articles                 記事一覧取得（page, per_page, query, tag）
GET    /api/articles/{item_id}       記事詳細取得

GET    /api/stocks                   自分のストック一覧取得
PUT    /api/stocks/{item_id}         ストックする
DELETE /api/stocks/{item_id}         ストック解除

GET    /api/drafts                   下書き一覧
POST   /api/drafts                   下書き新規作成
GET    /api/drafts/{id}              下書き詳細
PUT    /api/drafts/{id}              下書き編集
DELETE /api/drafts/{id}              下書き削除
POST   /api/drafts/{id}/publish      Qiitaへ新規投稿
PUT    /api/drafts/{id}/sync         Qiita記事を更新
```

## 技術スタック

- Python (FastAPI) + SQLite + HTML/CSS/JavaScript
- 認証: Qiita 個人アクセストークン（`.env`）

## セットアップ

```bash
cp .env.example .env
# .env を編集して QIITA_TOKEN を設定
pip install -r requirements.txt
uvicorn src.main:app --reload
```

`http://localhost:8000` で起動を確認する。

### Dev Container を使う場合

```bash
code .
# F1 → "Dev Containers: Reopen in Container"
claude
```

詳細は `AGENT_MASTER_PLAN.md` と `CLAUDE.md` を参照。

## プロジェクト構成

```
QiitaClientApp/
├── src/
│   ├── main.py           # FastAPIエントリーポイント（静的ファイル配信含む）
│   ├── database.py       # DB初期化
│   ├── models.py         # SQLAlchemyモデル
│   ├── schemas.py        # Pydanticスキーマ
│   ├── qiita_client.py   # Qiita API v2 クライアント
│   └── routers/          # APIルーター（auth, articles, stocks, drafts）
├── static/               # フロントエンド
│   ├── index.html        # 画面構成（記事一覧/詳細・ストック・下書きエディタ）
│   ├── style.css
│   ├── app.js
│   └── vendor/           # marked.js（CDN取得物を配置）
├── tests/                 # pytest
├── docs/                  # ドキュメント・記事ドラフト
├── data/                  # SQLiteファイル（gitignore対象）
└── AGENT_MASTER_PLAN.md   # Claude Code実行用マスタープラン
```

## ライセンス

MIT
