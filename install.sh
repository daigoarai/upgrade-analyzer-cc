#!/bin/bash
set -euo pipefail

COMMANDS_DIR="$HOME/.claude/commands"
SOURCE="$(dirname "$0")/upgrade-analyzer.md"

echo "upgrade-analyzer のインストールを開始します..."

if [ ! -f "$SOURCE" ]; then
    echo "エラー: upgrade-analyzer.md が見つかりません: $SOURCE"
    exit 1
fi

mkdir -p "$COMMANDS_DIR"
if [ $? -ne 0 ]; then
    echo "エラー: コマンドディレクトリの作成に失敗しました: $COMMANDS_DIR"
    exit 1
fi

cp "$SOURCE" "$COMMANDS_DIR/upgrade-analyzer.md"
if [ $? -ne 0 ]; then
    echo "エラー: upgrade-analyzer.md のコピーに失敗しました。"
    exit 1
fi

echo "インストール完了。"
echo "Claude Code を起動して /upgrade-analyzer コマンドが使えます。"
