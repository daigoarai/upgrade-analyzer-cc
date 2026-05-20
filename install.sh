#!/bin/bash
set -euo pipefail

COMMANDS_DIR="$HOME/.claude/commands"

echo "upgrade-analyzer のインストールを開始します..."

mkdir -p "$COMMANDS_DIR"
cp "$(dirname "$0")/upgrade-analyzer.md" "$COMMANDS_DIR/upgrade-analyzer.md"

echo "インストール完了。"
echo "Claude Code を起動して /upgrade-analyzer コマンドが使えます。"
