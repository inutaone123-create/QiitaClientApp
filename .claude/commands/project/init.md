プロジェクト初期化コマンドです。`{{...}}` プレースホルダーをすべて実際の値に置換します。

以下の手順で実行してください：

## Step 1: プレースホルダーの収集

以下のファイルから `{{...}}` パターンを検索し、ユニークなプレースホルダー一覧を抽出してください：
- `CLAUDE.md`
- `.devcontainer/devcontainer.json`

## Step 2: ユーザーへの確認

抽出したプレースホルダーを表示し、各プレースホルダーの値をユーザーに質問してください。

- `{{GIT_USER_NAME}}` — Gitユーザー名
- `{{GIT_USER_EMAIL}}` — Gitメールアドレス
- `{{GITHUB_REMOTE}}` — GitHubリモートURL（例: `https://github.com/user/QiitaClientApp`）
- `{{YEAR}}` — 実装年（例: `2026`）
- `{{LICENSE}}` — ライセンス名（デフォルト: `MIT`）

## Step 3: 置換の実行

ユーザーから値を受け取ったら、対象ファイル内のすべての該当プレースホルダーを置換してください。
値が未入力（スキップ）の場合はそのまま残してください。

## Step 4: Gitユーザー設定・リモート設定

`{{GIT_USER_NAME}}` / `{{GIT_USER_EMAIL}}` が入力された場合：

```bash
git config --global user.name "入力された名前"
git config --global user.email "入力されたメール"
```

`{{GITHUB_REMOTE}}` が入力された場合：

```bash
git remote add origin "入力されたURL" 2>/dev/null || git remote set-url origin "入力されたURL"
```

## Step 5: 完了報告

置換したプレースホルダーの一覧と、まだ未入力のプレースホルダーがあれば一覧を表示して完了を報告してください。
