Python (Sphinx) でAPIドキュメントを生成するコマンドです。

## Step 1: 環境確認

```bash
sphinx-build --version 2>/dev/null && echo "sphinx: OK" || echo "sphinx: 未インストール"
```

## Step 2: 出力ディレクトリの準備

```bash
mkdir -p docs/sphinx
```

## Step 3: Sphinx設定の初期化（未設定時のみ）

```bash
if [ ! -f docs/sphinx/conf.py ]; then
  sphinx-quickstart docs/sphinx \
    --quiet \
    --project="QiitaClientApp" \
    --author="{{GIT_USER_NAME}}" \
    --language=ja \
    --ext-autodoc \
    --ext-viewcode \
    --ext-napoleon
fi
```

## Step 4: APIドキュメント生成

```bash
sphinx-apidoc -o docs/sphinx . \
  --force \
  --separate \
  --module-first \
  --implicit-namespaces \
  -e 2>/dev/null

sphinx-build -b html docs/sphinx docs/sphinx/_build/html -q 2>&1 | tail -20
```

## Step 5: 結果の表示

```
## ドキュメント生成結果

| 対象 | ツール | 出力先 | 状態 |
|------|--------|--------|------|
| Python | Sphinx | docs/sphinx/_build/html/index.html | ✅ / ❌ |

### ⚠️ 警告（あれば）
- <警告内容>
```

## Step 6: ドキュメントコメント未記入の検出

docstring のない `def` / `class`（`__` 始まりは除外）を検索して報告してください。
未記入が多い場合は「`CLAUDE.md` のドキュメントコメント規約を参照して追記してください」と案内してください。
