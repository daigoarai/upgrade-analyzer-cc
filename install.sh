#!/bin/bash
set -euo pipefail

COMMANDS_DIR="$HOME/.claude/commands"
SOURCE="$(dirname "$0")/upgrade-analyzer.md"

echo "Installing upgrade-analyzer..."

if [ ! -f "$SOURCE" ]; then
    echo "Error: upgrade-analyzer.md not found: $SOURCE"
    exit 1
fi

mkdir -p "$COMMANDS_DIR"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create directory: $COMMANDS_DIR"
    exit 1
fi

cp "$SOURCE" "$COMMANDS_DIR/upgrade-analyzer.md"
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy upgrade-analyzer.md"
    exit 1
fi

echo "Installation complete."
echo "Start Claude Code and use the /upgrade-analyzer command."
