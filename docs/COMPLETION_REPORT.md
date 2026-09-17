# 完了報告書

**プロジェクト**: QiitaClientApp
**作成日**: 2026-09-17
**ブランチ**: main

## 実装概要

Qiita API v2 をラップしたローカルWebアプリ（QiitaClientApp）を、`AGENT_MASTER_PLAN.md` のPhase 0〜5に沿って実装した。Python (FastAPI) + SQLite + HTML/CSS/JavaScriptの構成で、①記事の取得・検索・閲覧、②ストックの一覧・追加・解除、③ローカル下書きの編集とQiitaへの新規投稿・更新、を一通り行えるようにしている。

認証はQiita個人アクセストークン（`.env`）方式とし、OAuthは採用していない。ストア公開は行わず、ローカルWebアプリ＋GitHubリポジトリで完結する方針で構築した。開発中に発見したXSSリスク（Qiita記事本文のMarkdown→HTML変換時の生HTML未サニタイズ）にはDOMPurifyを追加して対処済み。

## 実装フェーズと成果

| フェーズ | 内容 | 状態 |
|---------|------|------|
| Phase 0 | 環境構築・初期セットアップ | ✅ |
| Phase 1 | Qiita APIクライアント基盤 | ✅ |
| Phase 2 | データモデル & DB構築 | ✅ |
| Phase 3 | API実装 | ✅ |
| Phase 4 | フロントエンド実装 | ✅ |
| Phase 5 | 品質向上・仕上げ | ✅ |

## テスト結果

```
$ pytest --tb=short -q
...............................                                          [100%]
31 passed, 1 warning in 1.03s
```

pytest全31件がPASS。Qiita API呼び出しは全て `respx` でモック化しており、外部通信なしに再現可能。

## ファイル構成

```
QiitaClientApp/
├── src/
│   ├── main.py               # FastAPIエントリーポイント（lifespanでDB初期化、静的ファイル配信）
│   ├── database.py           # DB engine・セッション・init_db()
│   ├── models.py             # SQLAlchemyモデル（ManagedArticle, StockCache）
│   ├── schemas.py             # Pydanticスキーマ（DraftCreate/DraftUpdate/DraftOut）
│   ├── qiita_client.py        # Qiita API v2 認証付きクライアント
│   └── routers/
│       ├── auth.py            # GET /api/auth/verify
│       ├── articles.py        # GET /api/articles, /api/articles/{item_id}
│       ├── stocks.py          # GET/PUT/DELETE /api/stocks
│       └── drafts.py          # 下書きCRUD + publish/sync
├── static/
│   ├── index.html             # 記事一覧/詳細・ストック・下書きエディタの画面構成
│   ├── style.css
│   ├── app.js                 # API通信・状態管理・画面遷移
│   └── vendor/                # marked.js, DOMPurify（CDN取得物）
├── tests/                     # pytest（31件）
├── docs/
│   ├── sphinx/                 # Sphinx APIドキュメント（HTML生成済み）
│   └── COMPLETION_REPORT.md    # 本ファイル
├── data/                       # SQLiteファイル（gitignore対象）
├── requirements.txt
├── pytest.ini
└── AGENT_MASTER_PLAN.md
```

## APIエンドポイント一覧

```
GET    /api/auth/verify
GET    /api/articles
GET    /api/articles/{item_id}
GET    /api/stocks
PUT    /api/stocks/{item_id}
DELETE /api/stocks/{item_id}
GET    /api/drafts
POST   /api/drafts
GET    /api/drafts/{id}
PUT    /api/drafts/{id}
DELETE /api/drafts/{id}
POST   /api/drafts/{id}/publish
PUT    /api/drafts/{id}/sync
```

## ライセンス

MIT（`src/`配下の全ソースファイルにライセンスヘッダーを付与済み。CLAUDE.mdのテンプレートに準拠）

## 技術的知見・ハマりどころ

### Python / FastAPI / Qiita API v2
- `QiitaClient._request()` は `httpx.AsyncClient` を呼び出しごとに生成・破棄する設計（FastAPIのDIで`QiitaClient`自体がリクエストごとに新規生成されるため、コネクション使い回しの恩恵が薄く、respxとの相性を優先）。
- `respx.mock` はhttpxのトランスポート層をモンキーパッチするため、`QiitaClient`内部で都度`AsyncClient`を生成してもモック可能。
- Qiita APIのレート制限（429）はリトライせずそのまま`QiitaAPIError`として送出する方針。
- `init_db()`は`from src import models`を関数内で遅延importし、`database.py`と`models.py`の循環importを回避。
- FastAPIの起動時DB初期化は非推奨の`on_event("startup")`ではなく`lifespan`で実装。
- SQLiteのインメモリDB（`:memory:`）はコネクションごとに別DBになるため、テストでは`poolclass=StaticPool`が必須。
- 下書きのタグはDB上ではカンマ区切り文字列、APIレスポンスでは`list[str]`に変換。Qiita投稿ペイロードも都度組み立て。
- `publish`/`sync`はQiita API失敗時に`status`を`sync_error`に更新してからエラーを送出し、失敗状態をローカルにも記録。

### フロントエンド（Phase 4）
- Dev Container内にGUIブラウザが無いため、`playwright`（npm一時導入）+ `playwright install-deps`でheadless Chromiumを動かし実ブラウザ検証を実施。
- この検証で「戻るボタンで一覧が再読込されない」バグを発見・修正（タブ経由の遷移だけでは見逃していた）。
- `GET /`はPhase 4で`static/index.html`を返すよう変更（`FileResponse`）。静的アセットは`/static`にマウント。

### セキュリティ（Phase 5・コードレビューで発覚）
- Qiita記事本文・下書きプレビューを`marked.js`でHTML化する際、生HTMLがサニタイズされず描画されるXSSの余地を発見。
- `DOMPurify`（CDN取得）を追加し、`marked.parse()`の出力を必ず`DOMPurify.sanitize()`に通してから`innerHTML`へ差し込む方針に変更（マスタープランのCDN制約への例外追加はユーザー確認済み）。
- Playwrightで`<img src=x onerror="...">`を入力し、スクリプトが実行されないことを確認。

### ドキュメント生成（Sphinx）でのハマりどころ
- `sphinx-apidoc`はリポジトリルートではなく`src`パッケージのみを対象に実行する必要がある（ルート指定だと名前空間パッケージ化により不格好なモジュール名になる）。
- `Base`（`DeclarativeBase`）を`:members:`付きでフルドキュメント化すると、継承された`metadata`/`registry`属性の解決過程でSQLAlchemyの宣言的マッパー設定が早期確定され、後続の`ManagedArticle`定義が`AttributeError`で失敗する現象を発見。`src.database.rst`に`:exclude-members: metadata, registry`を追加して解消。

## コミット履歴

```
7aae5ba docs: Sphinx APIドキュメント生成基盤を追加
236b538 fix: コードレビュー指摘への対応（black整形・XSS対策）
99e1d28 feat: Phase 4 フロントエンドUIを実装
e7bc5b4 feat: Phase 3 記事取得・ストック・下書き管理APIを実装
913e70e feat: Phase 2 データモデル・DB基盤を実装
98e3608 feat: Phase 0-1 プロジェクト初期構築とQiita APIクライアント基盤を実装
```
