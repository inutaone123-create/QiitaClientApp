# QiitaClientApp

Qiita API v2 を利用した非公式クライアントアプリ（個人開発・記事ネタ用）。

ストア公開は行わず、ローカルWebアプリ + GitHubリポジトリで完結させることを方針とする。

## できること（予定）

- 記事の一覧取得・検索・詳細閲覧
- ストックの一覧・追加・解除
- ローカルで下書きを編集し、Qiitaへ新規投稿・更新

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
│   ├── main.py          # FastAPIエントリーポイント
│   ├── database.py      # DB初期化
│   ├── models.py        # SQLAlchemyモデル
│   ├── schemas.py       # Pydanticスキーマ
│   ├── qiita_client.py  # Qiita API v2 クライアント
│   └── routers/         # APIルーター
├── static/              # フロントエンド（HTML/CSS/JS）
├── tests/                # pytest
├── docs/                 # ドキュメント・記事ドラフト
├── data/                 # SQLiteファイル（gitignore対象）
└── AGENT_MASTER_PLAN.md  # Claude Code実行用マスタープラン
```

## ライセンス

MIT
