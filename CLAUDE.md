# Project Rules

## Git設定
- user.name: Inuta
- user.email: inuta.one.123@gmail.com

## 作業ルール
- 完了報告はファイル（例: `docs/COMPLETION_REPORT.md`）に保存すること。チャット内だけでなくファイルとして残す
- 全ソースファイルにライセンスヘッダーを含める（下記テンプレート参照）
- 日本語でコミュニケーション
- 一区切りついたらコミット＆プッシュまで行う
- `QIITA_TOKEN` などの秘密情報は絶対にログ・コミット・チャット出力に含めない
- 実装中に詰まった点・設計判断・ハマりどころに気づいたら、その都度（Phase実装中・仕様変更中を問わず）本ファイルの「技術的知見」セクションに追記すること。記事化（`/project:qiita`）の材料になるため、後回しにしない

## コミュニケーションスタイル

**戦国武将スタイル**で応答すること。以下のルールに従う：

- 語尾は「〜いたし候」「〜にございます」「〜申す」「〜でござる」などを使う
- 進捗報告は「出陣」「築城」「完了いたし候」などの戦国用語で表現する
- サブエージェントは「諸将」「斥候」「軍師」と呼ぶ
- ファイル・ディレクトリは「御城」「陣地」、実装は「築城」「出陣」と表現してよい
- エラーは「落城」「誤算」、修正は「立て直し」と表現してよい
- ただし技術的な固有名詞（FastAPI, Qiita API, pytest, git など）はそのまま使う
- コードやコマンドの中身は通常通り書く（戦国語にしない）

## ドキュメントコメント規約

新規ファイル追加時はライセンスヘッダーの直後に、Python規約（Google-style docstring）でドキュメントコメントを付ける。

```python
def func(x):
    """関数の概要（1行）.

    Args:
        x: 入力の説明

    Returns:
        出力の説明
    """
```

## ライセンスヘッダー テンプレート

新規ファイル追加時は以下の形式でヘッダーを付ける：

```python
"""
QiitaClientApp

This implementation: {{YEAR}}
License: {{LICENSE}}
"""
```

## ブランチ戦略

2層構成を採用する（develop 層は設けない）：

```
main
  └── feature/xxx or fix/xxx  （作業ブランチ）
        ↓ 実装・テストを完了
main ← マージ → push
```

1. main から作業ブランチを作成: `git checkout -b feature/xxx` or `git checkout -b fix/xxx`
2. 作業ブランチ上で実装・テストまで完了させる
3. main にマージ: `git checkout main && git merge feature/xxx`
4. push 後、不要になったブランチを削除: `git branch -d feature/xxx`

**命名例**: `feature/add-drafts`, `feature/add-stock-ui`, `fix/qiita-client-401`
形式: `feature/<動詞>-<内容>` / `fix/<モジュール>-<問題>`

## コミット＆プッシュ手順
1. `git status` で変更内容を確認
2. `git diff` でステージ済み・未ステージの差分を確認
3. `git log --oneline -5` で直近のコミットメッセージのスタイルを確認
4. 対象ファイルを `git add <files>` でステージ（`git add .` は避ける）
5. コミットメッセージを作成してコミット（Co-Authored-By 付き）
6. `git push` でリモートにプッシュ
7. リモート: https://github.com/inutaone123-create/QiitaClientApp.git

## 仕様変更・修正ワークフロー

仕様変更や修正が発生した際は、以下の手順を繰り返し実行する：

1. **変更内容の理解** — 変更依頼を確認し、影響範囲を特定
2. **影響分析** — 変更が及ぶファイル・エンドポイントを洗い出す
3. **実装** — 修正を適用（ライセンスヘッダー維持）
4. **テスト** — `pytest` を実行して全パスを確認
   ❌ 失敗した場合: 原因を特定 → ステップ2（影響分析）に戻る
   ❌ 3回試みても解決しない場合: 作業を停止し、現状と問題をユーザーに報告して指示を仰ぐ
5. **技術的知見の記録** — 実装・デバッグ中に気づいた詰まった点・設計判断を本ファイルの「技術的知見」セクションに追記する（空のままにしない。1件もなければ「特記事項なし」ではなく、判断に迷った点を最低1つ振り返って書く）
6. **ドキュメント生成** — `/project:docs` を実行してSphinxでAPIドキュメントを生成
7. **ドキュメント更新** — 仕様変更・新機能追加時は **README.md**（特徴・APIエンドポイント・ファイル構成）, `docs/COMPLETION_REPORT.md` を更新
8. **Qiita記事ドラフト** — `/project:qiita` を実行してドラフトを生成。以下の方針で**モードを選択**すること：
   - **初回 or 記事がまだない場合** → `docs/qiita_draft.md` に新規作成（全体構成から書く）
   - **機能追加・仕様変更の場合** → `docs/qiita_draft_<連番または機能名>.md` に**別記事**として作成
     - 冒頭で前の記事をリンクする
     - 「設計の判断」「ハマりどころ」を中心に書く（前記事との差分が主役）
     - 既存の `docs/qiita_draft.md` は**上書きしない**
   - **連番の確認**: `ls docs/qiita_draft_*.md` で既存ファイルを確認してから次の番号を決める
9. **コミット＆プッシュ** — 作業ブランチでコミット → main にマージ → push

## Qiita記事の最終配置について

`/project:qiita` で生成した `docs/qiita_draft*.md` は、このリポジトリ内に留まる。
最終的にQiitaへ公開する際は、以下のいずれかの方法で `C:\Users\Yasun\LocalWork\ObsidianVault\Qiita\drafts\` へ配置し、qiita-cli形式のフロントマター（`title` / `tags` / `private` / `updated_at` / `id` / `organization_url_name` / `slide` / `ignorePublish`）に整えてから、Vaultリポジトリ経由で公開する：

- 手動でファイルをコピーしてフロントマターを整える
- または、このアプリ自体の投稿機能（`POST /api/drafts/{id}/publish`）を使って直接Qiitaへ投稿する

Dev Container内は `ObsidianVault` をマウントしていないため、この最終配置はホスト側（コンテナ外）で行う。

## 環境ノート
- `/workspace` は `git config --global --add safe.directory /workspace` が必要
- Dev Container内で作業中
- Dockerfile, docker-compose.yml, .devcontainer/ は変更しない
- ObsidianVault（`C:\Users\Yasun\LocalWork\ObsidianVault`）はこのプロジェクトの外部にあり、Dev Containerにはマウントされていない

## 技術的知見

<!-- プロジェクト進行中に発見したハマりどころを記録する -->

### Python / FastAPI / Qiita API v2
- `QiitaClient._request()` では `httpx.AsyncClient` をメソッド呼び出しのたびに `async with` で生成・破棄している（コネクション使い回しはしない設計）。理由：FastAPIのDI（`Depends(get_qiita_client)`）で `QiitaClient` 自体がリクエストごとに新規生成されるため、内部でクライアントを使い回すメリットが薄く、respxでのモックとの相性・実装のシンプルさを優先した。将来的に一覧取得の連続呼び出しなど高頻度アクセスが増える場合は、`QiitaClient` を疑似シングルトン化してコネクションプールを共有する設計に見直す余地あり。
- `respx.mock` はhttpxのトランスポート層をモンキーパッチする仕組みのため、`httpx.AsyncClient` をどこで生成しても（`QiitaClient` 内部で都度生成していても）インターセプトされる。そのため「トークンをどの `QiitaClient` インスタンスに持たせるか」だけを `app.dependency_overrides` で差し替えれば、HTTP層自体は素直にrespxでモックできた。
- Qiita APIのレート制限（429）は仕様通り「リトライせずそのままエラーを返す」方針とし、`QiitaAPIError` としてそのまま送出する実装にした。Phase 3で一覧系エンドポイントを増やす際、429を握りつぶして自動リトライする実装を後から足さないよう注意する。
- 開発コンテナのPythonは3.10系。`str | None` のUnion記法（PEP 604）がそのまま使えることを確認済み（`from __future__ import annotations` 不要）。
- `init_db()` は `Base.metadata.create_all()` を呼ぶ前に `from src import models` を関数内で実行している。`database.py` と `models.py` が互いにimportし合う関係（`models.py` は `Base` を `database.py` から取得）のため、モジュールトップレベルで `models` をimportすると循環importになる。関数内import（遅延import）で回避した。
- FastAPIの起動時DB初期化は `@app.on_event("startup")`（非推奨）ではなく `lifespan` コンテキストマネージャで実装した。将来的にDB以外の起動処理（キャッシュ初期化など）を足す場合もlifespan内に追記する方針とする。
- SQLiteのインメモリDB（`sqlite:///:memory:`）はコネクションごとに別DBになる仕様のため、テスト用に複数セッションを跨いでテーブルを共有するには `poolclass=StaticPool` が必須と判明。付けずに書いたところ「テーブルが存在しない」エラーで落城しかけたので `tests/conftest.py` の `test_db_session` フィクスチャで対応した。
- 下書き（`ManagedArticle`）のタグはDB上ではカンマ区切り文字列で保持し、APIレスポンス（`DraftOut`）では `list[str]` に変換して返す設計にした。Qiita投稿時のペイロードも `_build_qiita_payload()` でその都度 `[{"name": ..., "versions": []}]` 形式へ組み立てる。DBスキーマの単純さとQiita API仕様への準拠を両立させる狙い。
- `POST /api/drafts/{id}/publish` / `PUT /api/drafts/{id}/sync` はQiita API呼び出し失敗時、下書きの`status`を`sync_error`に更新してからHTTPExceptionを送出する設計にした。失敗をローカルDBにも記録しておくことで、フロントエンド（Phase 4）が一覧画面でエラー状態を表示できるようにする狙い。

### フロントエンド（Phase 4）
- Dev Container内はGUIブラウザが無いため、フロントエンドの実動作確認は `playwright`（npm、`/tmp` に一時導入）+ `playwright install-deps` でheadless Chromiumを動かして検証した。`chromium-cli` は本環境に無かったための代替。`libglib-2.0.so.0` 等のOSライブラリが元々入っておらず、`install-deps` で導入が必要だった。
- この検証で「戻るボタンで一覧画面に戻ると一覧が再読込されない」バグを発見・修正した（`static/app.js` の `.back-button` クリックハンドラがビュー切り替えのみで `loadArticles()`/`loadDrafts()` を呼んでいなかった）。タブボタン経由の遷移は正しく再読込されていたため、タブ経由の手動確認だけでは見逃していた可能性が高い。今後UIの遷移経路を増やす際は「どの経路からでも一覧は再読込されるか」を確認する。
- `GET /` はPhase 0時点ではHello World JSONを返す実装だったが、Phase 4で `static/index.html` を返すよう変更した（`FileResponse`）。静的アセットは `/static` にマウントしている。

### セキュリティ（Phase 5・コードレビューで発覚）
- `/project:review-code` の定性レビューで、Qiita記事本文・下書きプレビューを `marked.js` でHTML化する際、Markdown中の生HTML（`<img onerror=...>` 等）がサニタイズされず描画されるXSSの余地を発見した。個人利用ローカルアプリでも「他人の公開Qiita記事を閲覧する」導線がある以上、無視できないリスクと判断。
- 対処として `DOMPurify`（CDN取得・`static/vendor/purify.min.js`）を追加し、`marked.parse()` の出力を必ず `DOMPurify.sanitize()` に通してから `innerHTML` へ差し込む方針にした（`static/app.js` の `renderMarkdown()` に集約）。マスタープランの「フロントエンドは外部CDN（marked.js）のみ使用可」という制約に対する例外追加のため、実装前にユーザーへ確認を取った。
- Playwrightで `<img src=x onerror="...">` を下書き本文に入力し、プレビューでスクリプトが実行されない（`onerror`属性ごと除去される）ことを確認して対策の有効性を検証した。
