#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/gergogyulai/toki.git"
INSTALL_DIR="$HOME/.toki"
BIN_PATH="$HOME/.local/bin"

echo "📦 Setting up Toki CLI..."

if ! command -v uv &> /dev/null; then
  echo "❌ uv is not installed. Install from: https://docs.astral.sh/uv/"
  exit 1
fi

# Clone or update
if [ ! -d "$INSTALL_DIR" ]; then
  git clone "$REPO_URL" "$INSTALL_DIR"
else
  echo "🔄 Updating existing repo..."
  git -C "$INSTALL_DIR" pull
fi

cd "$INSTALL_DIR"

# Install for current user
uv pip install --user -e .

echo ""

# Check PATH
if [[ ":$PATH:" != *":$BIN_PATH:"* ]]; then
  echo "⚠️  $BIN_PATH is not in your PATH."
  echo "   Add this line to ~/.bashrc or ~/.zshrc:"
  echo "   export PATH=\"$BIN_PATH:\$PATH\""
fi

echo "✅ Done! Run 'toki --help'"