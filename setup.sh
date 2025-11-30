#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/gergogyulai/toki.git"
INSTALL_DIR="$HOME/.toki"
VENV_DIR="$HOME/.local/toki-venv"
BIN_DIR="$HOME/.local/bin"
CMD_PATH="$VENV_DIR/bin/toki"

echo "📦 Setting up or updating Toki CLI..."

if ! command -v uv &>/dev/null; then
  echo "❌ uv is required. Install from https://docs.astral.sh/uv/"
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

# Create venv if needed
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Creating Toki virtual environment..."
  uv venv "$VENV_DIR"
fi

# Install or update only if repo changed
HASH_FILE="$VENV_DIR/.toki_install_hash"
CURRENT_HASH=$(cd "$INSTALL_DIR" && git rev-parse HEAD)
LAST_HASH=$(cat "$HASH_FILE" 2>/dev/null || echo "none")

if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
  echo "📥 Installing / updating Toki package..."
  # Unset PIP_USER to avoid conflicts with uv
  env -u PIP_USER uv pip install --python "$VENV_DIR/bin/python" -e "$INSTALL_DIR"
  echo "$CURRENT_HASH" >"$HASH_FILE"
else
  echo "✅ Already up to date ($CURRENT_HASH)"
fi

# Ensure symlink to path
mkdir -p "$BIN_DIR"
ln -sf "$CMD_PATH" "$BIN_DIR/toki"

# PATH reminder
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo ""
  echo "⚠️  $BIN_DIR is not in your PATH."
  echo "   Add this line to your ~/.bashrc or ~/.zshrc:"
  echo "   export PATH=\"$BIN_DIR:\$PATH\""
  echo ""
fi

echo "🎉 Toki CLI ready! Try: toki --help"