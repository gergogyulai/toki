#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/gergogyulai/toki.git"
INSTALL_DIR="$HOME/.toki"
VENV_DIR="$HOME/.local/toki-venv"
BIN_DIR="$HOME/.local/bin"
CMD_PATH="$VENV_DIR/bin/toki"

echo "📦 Setting up or updating Toki CLI..."

# Ensure uv is installed
if ! command -v uv &> /dev/null; then
  echo "❌ uv not found. Please install it first:"
  echo "   https://docs.astral.sh/uv/"
  exit 1
fi

# Clone or update repository
if [ ! -d "$INSTALL_DIR/.git" ]; then
  echo "🔹 Cloning Toki repository..."
  git clone "$REPO_URL" "$INSTALL_DIR"
else
  echo "🔄 Updating existing repository..."
  git -C "$INSTALL_DIR" pull --rebase --autostash || true
fi

# Ensure venv exists
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Creating dedicated Toki environment..."
  uv venv "$VENV_DIR"
fi

# Activate and check if reinstall needed
source "$VENV_DIR/bin/activate"

# Determine if source changed (simplified cache check)
HASH_FILE="$VENV_DIR/.toki_install_hash"
CURRENT_HASH=$(cd "$INSTALL_DIR" && git rev-parse HEAD)
LAST_HASH=$(cat "$HASH_FILE" 2>/dev/null || echo "none")

if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
  echo "📥 Installing / updating Toki package..."
  uv pip install -e "$INSTALL_DIR"
  echo "$CURRENT_HASH" > "$HASH_FILE"
else
  echo "✅ Already up to date (commit $CURRENT_HASH)"
fi

# Ensure BIN_DIR exists and symlink CLI
mkdir -p "$BIN_DIR"
ln -sf "$CMD_PATH" "$BIN_DIR/toki"

# PATH hint
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo ""
  echo "⚠️  $BIN_DIR is not in your PATH."
  echo "   Add this line to your ~/.bashrc or ~/.zshrc:"
  echo "   export PATH=\"$BIN_DIR:\$PATH\""
  echo ""
fi

echo "🎉 Toki CLI is ready! Run: toki --help"