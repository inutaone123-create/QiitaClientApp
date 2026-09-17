プロジェクトのフェーズ進捗を確認するコマンドです。

以下の手順で現在の状態を調査・表示してください：

## Step 1: 基本情報の確認

```bash
git log --oneline -20
git status
git branch
```

## Step 2: AGENT_MASTER_PLAN.md のフェーズ一覧を読む

`AGENT_MASTER_PLAN.md` を読み込み、Phase 0〜5 の各タスクのチェック状態（`- [ ]` / `- [x]`）を確認してください。

## Step 3: 各フェーズの完了判定

| フェーズ | 完了の判定基準 |
|---------|--------------|
| Phase 0 | `uvicorn src.main:app` が起動し `src/main.py` が存在する |
| Phase 1 | `src/qiita_client.py` が存在し、`/api/auth/verify` が実装されている |
| Phase 2 | `src/models.py` に `ManagedArticle` が定義され、DBが生成される |
| Phase 3 | `src/routers/articles.py`, `stocks.py`, `drafts.py` が存在する |
| Phase 4 | `static/index.html`, `static/app.js` が実装されている |
| Phase 5 | `docs/COMPLETION_REPORT.md` が存在し、`pytest` が全てPASSする |

## Step 4: プレースホルダーの残存確認

```bash
grep -r "{{" CLAUDE.md .devcontainer/ 2>/dev/null | grep -v "^Binary"
```

未置換のプレースホルダーが残っている場合は警告を表示してください。

## Step 5: テスト状態の確認

```bash
pytest --tb=no -q 2>/dev/null
```

## Step 6: 結果の表示

以下の形式で表示してください：

```
## プロジェクト進捗状況

**ブランチ**: main / feature/xxx
**最新コミット**: <メッセージ>

### フェーズ進捗
- [x] Phase 0: 環境構築・初期セットアップ
- [ ] Phase 1: Qiita APIクライアント基盤
- [ ] Phase 2: データモデル & DB構築
- [ ] Phase 3: API実装
- [ ] Phase 4: フロントエンド実装
- [ ] Phase 5: 品質向上・仕上げ

### ⚠️ 未置換プレースホルダー
- {{GIT_USER_NAME}} — CLAUDE.md
（なければ「✅ なし」）

### テスト状態
- pytest: X passed / Y failed / 未実行
```
