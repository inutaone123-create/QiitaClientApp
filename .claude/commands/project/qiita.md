Qiita投稿用の記事ドラフトを `docs/qiita_draft.md` に生成するコマンドです。

## Step 1: プロジェクト情報の収集

以下を読み込んでください：
- `AGENT_MASTER_PLAN.md`（プロジェクト目標・フェーズ・API仕様）
- `docs/COMPLETION_REPORT.md`（存在する場合）
- `CLAUDE.md`
- `README.md`

```bash
git log --oneline | head -20
```

## Step 2: コード例の抜粋

`src/qiita_client.py`, `src/routers/*.py` から、記事で紹介するのに適したコード例を最大2〜3個抜粋してください。

## Step 3: テスト結果の取得

```bash
pytest --tb=no -q 2>/dev/null | tail -5
```

## Step 4: docs/qiita_draft.md の生成

以下の構成でドラフトを生成してください：

```markdown
---
title: 【TODO: タイトルを記入】
tags:
  - Python
  - FastAPI
  - Qiita
  - API
emoji: 📮
type: tech
topics: []
published: false
---

## はじめに

<!-- TODO: なぜQiitaの非公式クライアントを作ったか（記事ネタ用と割り切った経緯）を記述 -->

## この記事で作るもの

<!-- AGENT: AGENT_MASTER_PLAN.md のゴール・機能一覧をもとに記述 -->

## 環境

| 項目 | バージョン |
|------|-----------|
| OS | Ubuntu 22.04 (Dev Container) |
| Python | 3.x |
| FastAPI | 0.115.x |

## Qiita API v2 との連携

<!-- AGENT: 認証（個人アクセストークン）・エンドポイント設計・レート制限への配慮を記述 -->

### 認証・APIクライアント

```python
# TODO: src/qiita_client.py のコード例を挿入
```

### 記事取得・ストック操作

```python
# TODO: src/routers/articles.py または stocks.py のコード例を挿入
```

### 投稿・更新

```python
# TODO: src/routers/drafts.py のコード例を挿入
```

## 動作確認

```
TODO: pytest の出力を挿入
```

## ハマりどころ

<!-- AGENT: CLAUDE.md の技術的知見セクションから転記 -->

-

## まとめ

-
-
-

## 参考

- [Qiita API v2 documentation](https://qiita.com/api/v2/docs)
```

## Step 5: TODO の一覧表示

生成後、`<!-- TODO:` と `# TODO:` を検索して一覧表示してください。

## Step 6: 既存ファイルの扱い

`docs/qiita_draft.md` がすでに存在する場合は、上書きするか確認してから実行してください。

## Step 7: 最終配置についての案内

生成完了後、以下を案内してください：

> このドラフトはリポジトリ内 (`docs/qiita_draft.md`) に留まります。TODOを埋めて完成させたら、
> ホスト側（Dev Container外）で `C:\Users\Yasun\LocalWork\ObsidianVault\Qiita\drafts\` にコピーし、
> qiita-cli形式のフロントマター（`id` / `updated_at` / `organization_url_name` / `slide` / `ignorePublish`）を
> 追加してからVaultリポジトリ経由で公開してください。
