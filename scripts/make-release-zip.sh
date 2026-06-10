#!/bin/bash
set -euo pipefail

# 配布用ZIPを生成する。
# 解凍時のトップフォルダ名を upgrade-analyzer-cc/ に固定するため git archive --prefix を使う。
# 誰がどこで解凍しても必ず同じフォルダ名になり、相手側の手順が壊れない。

PREFIX="upgrade-analyzer-cc"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$REPO_ROOT/dist"
OUT_ZIP="$OUT_DIR/${PREFIX}.zip"

cd "$REPO_ROOT"

mkdir -p "$OUT_DIR"

# HEAD の追跡ファイルのみを対象にするため、未追跡の一時ファイル（tmp-*, reports など）は混入しない。
git archive --format=zip --prefix="${PREFIX}/" -o "$OUT_ZIP" HEAD

echo "Created: $OUT_ZIP"
echo "Top folder when unzipped: ${PREFIX}/"
