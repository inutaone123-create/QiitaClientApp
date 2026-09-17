完了報告書（`docs/COMPLETION_REPORT.md`）を生成するコマンドです。

## Step 1: 情報収集

```bash
git log --oneline
git diff --stat HEAD~5 HEAD 2>/dev/null || git diff --stat HEAD
date '+%Y-%m-%d'
```

`AGENT_MASTER_PLAN.md` と `CLAUDE.md` を読み込んでください。

## Step 2: テスト結果の取得

```bash
pytest --tb=short -q 2>/dev/null
```

## Step 3: docs/ ディレクトリの確認・作成

```bash
mkdir -p docs
```

## Step 4: COMPLETION_REPORT.md の生成

```markdown
# 完了報告書

**プロジェクト**: QiitaClientApp
**作成日**: YYYY-MM-DD
**ブランチ**: main

## 実装概要

（AGENT_MASTER_PLANの目標セクションをもとに、何を実装したか1〜3段落で記述）

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
（テストコマンドの出力をそのまま貼り付け）
```

## ファイル構成

（`find . -type f | grep -v '\.git' | sort` の結果をもとに主要ファイルを列挙）

## ライセンス

（CLAUDE.md のライセンス情報をもとに記載）

## 技術的知見・ハマりどころ

（CLAUDE.md の技術的知見セクションから転記。空なら「特記事項なし」）

## コミット履歴

（git log --oneline の出力）
```

## Step 5: 既存ファイルの扱い

`docs/COMPLETION_REPORT.md` がすでに存在する場合は、上書きするか確認をユーザーに求めてから実行してください。

## Step 6: 完了報告

ファイル生成後、`docs/COMPLETION_REPORT.md` のパスを表示して完了を報告してください。
