#!/bin/bash
# This script sets up the local development environment for the MarkdownLint MCP server.
# It is intended for developers working on the server's source code.
set -e

echo "--- Initializing Python virtual environment using uv ---"
# `uv venv` will create a .venv directory and use the Python version from pyproject.toml
uv venv

echo ""
echo "--- Installing Python dependencies from pyproject.toml ---"
# This installs the current project in "editable" mode (-e) so that changes to the
# source code are immediately available.
uv pip install -e .

echo ""
echo "--- Installing Node.js dependency: markdownlint-cli ---"

# 1. Source nvm if it exists, to ensure we use the nvm-managed node and npm.
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    echo "Sourcing nvm from $HOME/.nvm/nvm.sh"
    . "$HOME/.nvm/nvm.sh"
fi

# 2. Check if npm is installed and available.
if ! command -v npm &> /dev/null; then
    echo "Error: npm command not found. Please install Node.js and npm, then run this script again."
    exit 1
fi

# 3. Install the linter locally.
echo "Attempting to install markdownlint-cli locally..."
npm install markdownlint-cli

echo ""
echo "--- Development Setup Complete! ---"
echo "A .venv virtual environment has been created and all dependencies are installed."
echo "You can now run the server for local testing with: uv run python -m src.markdownlint_mcp.main"
echo "To use the locally installed linter, you may need to run commands like:"
echo "npx markdownlint-cli ..."
