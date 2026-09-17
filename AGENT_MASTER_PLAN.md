# 🌐 AGENT MASTER PLAN — QiitaClientApp（Qiita非公式クライアント）

## プロジェクト概要

| 項目 | 内容 |
|------|------|
| プロジェクト名 | QiitaClientApp |
| 目的 | Qiita API v2 を利用した非公式クライアントアプリの開発。開発過程自体をQiita記事のネタにする（自分では常用しない想定） |
| 技術スタック | Python (FastAPI) + SQLite + HTML/CSS/JavaScript |
| 公開方針 | ストア公開なし。ローカルWebアプリ + GitHubリポジトリで完結 |
| 認証方式 | Qiita 個人アクセストークン（`.env` に保存、OAuth不要） |
| 対象ユーザー | 自分一人（記事ネタ用の実験プロジェクト） |

## ゴール

Qiita API v2 をラップしたローカルWebアプリを構築し、①記事の取得・検索・閲覧、②ストックの一覧・追加・解除、③自分の記事の新規投稿・更新、を一通り行えるようにする。

---

## フェーズ設計

### Phase 0：環境構築・初期セットアップ

**目標:** プロジェクト構成を整備し、FastAPIが起動できる状態にする

**タスク:**
- [x] Pythonプロジェクト構成を作成（`src/`, `src/routers/`, `tests/`, `static/`）
- [x] `requirements.txt` を作成（fastapi, uvicorn, sqlalchemy, httpx, python-dotenv, pydantic, pytest）
- [x] `.env.example` を作成（`QIITA_TOKEN=`）。実体の `.env` は `.gitignore` 対象
- [x] FastAPIのエントリーポイント（`src/main.py`）を作成
- [x] `http://localhost:8000` でHello Worldが返ることを確認

**完了条件:** `uvicorn src.main:app --reload` で起動し、ブラウザからアクセスできる

---

### Phase 1：Qiita APIクライアント基盤

**目標:** Qiita API v2 への認証付きリクエストをラップするクライアントモジュールを作る

**タスク:**
- [x] `src/qiita_client.py` — httpxベースのAPIクライアント
  - `get_authenticated_user()` / `list_items()` / `get_item(item_id)`
  - `list_stocks()` / `stock_item(item_id)` / `unstock_item(item_id)`
  - `create_item(payload)` / `update_item(item_id, payload)`
- [x] `.env` から `QIITA_TOKEN` を読み込む処理（`python-dotenv`）
- [x] トークン未設定・無効時のエラーハンドリング（401時にわかりやすいメッセージ）
- [x] Qiita APIレート制限（認証済み1000 req/h）を意識し、429時はリトライせずエラーをそのまま返す方針を明記
- [x] `GET /api/auth/verify` エンドポイントで動作確認（`/api/v2/authenticated_user` をプロキシ）

**完了条件:** 有効なトークンで認証ユーザー情報が取得できる。無効トークンで適切なエラーが返る

---

### Phase 2：データモデル & DB構築（ローカル管理記事）

**目標:** 投稿・更新用のローカル管理記事（下書き）のテーブル設計と初期化

**データモデル:**

```
ManagedArticle（管理対象記事）
  - id: INTEGER PRIMARY KEY
  - qiita_id: TEXT NULL          -- Qiita側記事ID（未投稿はNULL）
  - title: TEXT NOT NULL
  - body: TEXT                   -- Markdown本文
  - tags: TEXT                   -- カンマ区切り（最大5個、Qiita仕様に準拠）
  - qiita_private: BOOLEAN       -- Qiita側の限定共有フラグ
  - status: TEXT                 -- 'draft' | 'published' | 'sync_error'
  - qiita_url: TEXT NULL
  - created_at: DATETIME
  - updated_at: DATETIME

StockCache（ストック一覧のローカルキャッシュ、表示高速化用）
  - qiita_item_id: TEXT PRIMARY KEY
  - title: TEXT
  - url: TEXT
  - tags: TEXT
  - cached_at: DATETIME
```

**タスク:**
- [x] SQLAlchemyでモデル定義（`src/models.py`）
- [x] DBの初期化処理（`src/database.py`）
- [x] アプリ起動時にテーブルが自動作成されること確認

**完了条件:** DBファイル（`data/qiitaclient.db`）が生成され、モデルの読み書きができる

---

### Phase 3：API実装（記事取得・ストック・投稿管理）

**目標:** 記事取得・ストック操作・ローカル管理記事CRUD・Qiitaへの投稿/更新のREST APIを実装する

**APIエンドポイント:**

```
# 認証確認
GET    /api/auth/verify              -- トークン有効性確認

# 記事取得（Qiita本体をプロキシ）
GET    /api/articles                 -- 記事一覧取得（page, per_page, query, tag でフィルタ）
GET    /api/articles/{item_id}       -- 記事詳細取得

# ストック操作
GET    /api/stocks                   -- 自分のストック一覧取得
PUT    /api/stocks/{item_id}         -- ストックする
DELETE /api/stocks/{item_id}         -- ストック解除

# ローカル管理記事（下書き）
GET    /api/drafts                   -- 管理記事一覧
POST   /api/drafts                   -- 新規下書き作成
GET    /api/drafts/{id}              -- 下書き詳細
PUT    /api/drafts/{id}              -- 下書き編集
DELETE /api/drafts/{id}              -- 下書き削除
POST   /api/drafts/{id}/publish      -- Qiitaへ新規投稿（POST /api/v2/items）
PUT    /api/drafts/{id}/sync         -- Qiita記事を更新（PATCH /api/v2/items/{qiita_id}）
```

**タスク:**
- [x] Pydanticスキーマ定義（`src/schemas.py`）
- [x] 記事取得ルーター（`src/routers/articles.py`）
- [x] ストック操作ルーター（`src/routers/stocks.py`）
- [x] 下書き管理ルーター（`src/routers/drafts.py`）
- [x] 全エンドポイントをpytestで動作確認（Qiita API呼び出しはモック化）

**完了条件:** 全APIが正常レスポンスを返す（pytestで確認、外部API呼び出しはhttpxモックで代替）

---

### Phase 4：フロントエンド実装

**目標:** ブラウザで使える記事一覧・詳細・ストック・投稿編集UIを作成する

**機能:**
- 記事一覧（検索ボックス・タグフィルタ）とページネーション
- 記事詳細表示（Markdown→HTML、`marked.js`使用）
- ストックボタン（一覧・詳細画面から追加/解除、状態を即時反映）
- 下書き一覧・エディタ（タイトル・タグ・Markdown本文、プレビュー付き）
- 「投稿する」「更新する」ボタン（下書き→Qiitaへ反映、結果URLを表示）

**タスク:**
- [x] `static/index.html` に画面構成を実装（一覧/詳細/ストック/下書きエディタの切り替え）
- [x] `static/style.css` でスタイリング
- [x] `static/app.js` でAPIとの通信・状態管理
- [x] `marked.js`（CDN、`static/vendor/`に配置）でMarkdownプレビュー（+ コードレビュー指摘によりDOMPurifyでのサニタイズを追加）

**完了条件:** ブラウザで記事一覧・詳細・ストック操作・下書き投稿がすべて動く

---

### Phase 5：品質向上・仕上げ

**目標:** テスト・ドキュメント・仕上げ

**タスク:**
- [x] pytestで主要ルートをテスト（`tests/test_articles.py`, `tests/test_stocks.py`, `tests/test_drafts.py`）— Qiita API呼び出しは `httpx` のモック/`respx` を使用（31件PASS、ホストでの再実行でも確認済み）
- [x] 起動手順・`.env`設定方法を `README.md` に記述
- [x] エラーハンドリング確認（無効トークン・存在しない記事IDなど）
- [x] `/project:review-code` でコードレビュー実施（XSSリスクを検出しDOMPurify対応）
- [x] `/project:docs` を実行してSphinxでAPIドキュメントを生成
- [x] `/project:qiita` を実行して `docs/qiita_draft.md` を生成（このプロジェクトの開発過程を記事化）
- [ ] 完成した記事ドラフトを `ObsidianVault/Qiita/drafts/` にコピーし、qiita-cli形式のフロントマターに整える
  （Dev Container外・ホスト側での作業。Vaultは本コンテナのマウント対象外のため。**未実施** — `docs/qiita_draft.md` は完成済みなので、コピーするだけの状態）

**完了条件:** `pytest` がすべてPASS、READMEの手順で誰でも起動できる

---

## 制約・ルール

- `Dockerfile`, `docker-compose.yml`, `.devcontainer/` は変更しない
- `CLAUDE.md` のルールに従って作業する
- フロントエンドは外部CDN（marked.js）のみ使用可、npmビルド不要
- DBはSQLiteファイル1つ（`data/qiitaclient.db`）に集約。ローカル管理記事（下書き）専用で、Qiita本体のデータはキャッシュ以外保持しない
- `QIITA_TOKEN` は `.env` にのみ保存し、絶対にコミットしない（`.gitignore` 対象）
- Qiita API v2 レート制限（認証済み1000 req/h）を超えないよう、一覧取得は `per_page` を適切に設定する
- ストア公開はしない。ローカルWebアプリ + GitHubリポジトリで完結させる
- 記事タグは最大5個まで（Qiita仕様）

## 将来の拡張メモ（今回は実装しない）

- OAuth認証への切り替え
- 複数Qiitaアカウント対応
- ObsidianVaultとの直接連携（Vault内Markdownの自動インポート等）
- コメント・LGTM機能への対応
- Electronパッケージ化
