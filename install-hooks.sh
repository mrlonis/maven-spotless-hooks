#!/bin/sh
set -e

HOOK_DIR=".git/hooks"
SRC_DIR=".hooks"

if [ ! -d "$HOOK_DIR" ]; then
  echo "Error: .git directory not found. Have you run 'git init'?"
  exit 1
fi

echo "Installing Git hooks..."

cp "$SRC_DIR/pre-commit" "$HOOK_DIR/pre-commit"
cp "$SRC_DIR/post-commit" "$HOOK_DIR/post-commit"

chmod +x "$HOOK_DIR/pre-commit"
chmod +x "$HOOK_DIR/post-commit"

echo "Git hooks installed successfully."
