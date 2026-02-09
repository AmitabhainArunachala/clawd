#!/bin/bash
#
# Setup script for arXiv Daily Brief automation
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "🤖 Setting up arXiv Daily Brief..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📍 Python version: $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv "$VENV_DIR"

# Activate and install dependencies
echo "📥 Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

# Create directories
echo "📁 Creating directories..."
mkdir -p "$SCRIPT_DIR/output"
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/templates"

# Make scripts executable
chmod +x "$SCRIPT_DIR/run_daily.sh"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.json with your settings"
echo "2. Set ANTHROPIC_API_KEY environment variable for AI synthesis (optional)"
echo "3. Test the pipeline: ./run_daily.sh"
echo "4. Add to crontab: crontab -e"
echo ""
echo "Example crontab entry (daily at 6 AM):"
echo "0 6 * * * cd $SCRIPT_DIR && ./run_daily.sh >> $SCRIPT_DIR/logs/cron.log 2>&1"
echo ""
echo "🪷 Ready to automate!"
