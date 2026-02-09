#!/bin/bash
#
# arXiv Daily Brief - Cron Job Runner
# Run this script daily to generate and publish the newsletter
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
LOG_DIR="$SCRIPT_DIR/logs"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/brief_$DATE.log"

# Create directories
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================"
log "🤖 arXiv Daily Brief - Starting Run"
log "========================================"

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    log "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    source "$VENV_DIR/bin/activate"
fi

# Change to script directory
cd "$SCRIPT_DIR"

# Run the pipeline (using 2 days to ensure we get content even on slow days)
log "🚀 Running pipeline..."
python3 src/pipeline.py --days 2 --max-papers 30 --top-n 5 --skip-publish >> "$LOG_FILE" 2>&1

# Check if successful
if [ $? -eq 0 ]; then
    log "✅ Pipeline completed successfully"
    
    # Copy latest to a known location for easy access
    if [ -f "$SCRIPT_DIR/output/latest.md" ]; then
        cp "$SCRIPT_DIR/output/latest.md" "$SCRIPT_DIR/LATEST_BRIEF.md"
        log "📄 Latest brief copied to LATEST_BRIEF.md"
    fi
    
    # Optional: Send notification (if configured)
    # Uncomment and configure if you want notifications
    # curl -s -X POST "YOUR_WEBHOOK_URL" \
    #     -H "Content-Type: application/json" \
    #     -d "{\"text\":\"✅ arXiv Daily Brief generated for $DATE\"}" > /dev/null
    
else
    log "❌ Pipeline failed!"
    exit 1
fi

log "========================================"
log "🪷 Run Complete"
log "========================================"
