# AGENT EXECUTION GUIDE
# Dev Container環境でのClaude Code実行手順

---

## 🎬 使い方

### ステップ1: `.env` を用意する

```bash
cp .env.example .env
# .env を編集して QIITA_TOKEN を設定（Phase 1以降で必要）
```

`QIITA_TOKEN` は https://qiita.com/settings/applications で発行した個人アクセストークン。
`.env` は `.gitignore` 対象なのでコミットされない。

### ステップ2: Dev Containerで開く

```bash
code .
# F1 → "Dev Containers: Reopen in Container"
# （初回はDockerイメージのビルドに数分かかります）
```

### ステップ3: Dev Container内でClaude Codeを実行

```bash
# VSCode内蔵ターミナル（既にコンテナ内）
claude
```

**Claude Codeへのプロンプト（コピー&ペースト）**:

```
Dev Container内で作業中です。

AGENT_MASTER_PLAN.md を読んで、Phase 0 から順番に実行してください。

Dockerfile、docker-compose.yml、.devcontainer/ は既に存在するので、
それらは変更せず、他のファイルを作成・編集してください。

CLAUDE.md のルールに従って作業してください。
```

---

## 🤖 サブエージェント

`.claude/agents/` に3つのサブエージェントが定義されている。タスクの重さに応じてClaude が自動的に委譲する。

| エージェント | モデル | 使いどころ |
|-------------|--------|-----------|
| `explorer` | Haiku | ファイル検索・コード確認・構造把握 |
| `implementer` | Sonnet | 通常の実装・テスト修正・バグ修正 |
| `architect` | Opus | 設計・計画・複雑な技術的意思決定 |

メインの会話は `sonnet`（`.claude/settings.json`）で動く。

---

## 🛠️ スラッシュコマンド一覧

| コマンド | タイミング | 内容 |
|---------|-----------|------|
| `/project:init` | プロジェクト開始時（1回） | `{{...}}` を対話形式で一括置換、git / remote 設定 |
| `/project:status` | いつでも | フェーズ進捗・未置換プレースホルダー・テスト状態を表示 |
| `/project:license-check` | 実装中・完了前 | ライセンスヘッダー欠けファイルを検出、自動追加を提案 |
| `/project:review-code` | 実装完了後 | 静的解析＋定性レビュー |
| `/project:docs` | 実装完了後 | Sphinxを実行してAPIドキュメントを生成 |
| `/project:report` | フェーズ完了時 | `docs/COMPLETION_REPORT.md` を自動生成 |
| `/project:qiita` | 最終化時（任意） | `docs/qiita_draft.md` にQiita投稿用記事ドラフトを生成 |

### 典型的な使用順序

```
/project:init          # 1. プロジェクト初期化（Git設定・ライセンス年など）
  ↓ Phase 0〜4 実装 ...
/project:status         # 2. 進捗確認（随時）
/project:license-check  # 3. ヘッダー漏れ確認（随時）
/project:review-code    # 4. コードレビュー
/project:docs           # 5. APIドキュメント生成
/project:report         # 6. 完了報告書生成
/project:qiita          # 7. Qiita記事ドラフト生成（任意）
```

`/project:qiita` で生成したドラフトの最終配置（ObsidianVaultへのコピー・qiita-cli形式への整形・公開）は、`CLAUDE.md` の「Qiita記事の最終配置について」を参照し、コンテナ外（ホスト側）で行う。

---

## ✅ プロジェクト開始チェックリスト

- [ ] `.env` を作成し `QIITA_TOKEN` を設定した
- [ ] Dev Container でビルドが成功した（初回は数分かかる）
- [ ] `claude` コマンドが起動できることを確認した
- [ ] `/project:init` を実行して `{{...}}` プレースホルダー（Git設定・年・ライセンス）を一括置換した
- [ ] `/project:status` で未置換プレースホルダーがないことを確認した
- [ ] Claude Code にキックオフプロンプトを渡して Phase 0 から実行開始した
