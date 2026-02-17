#!/bin/bash
# ═════════════════════════════════════════════════════════════════════════════
# OPENCLAW TPS — Installation Script
# Version: 1.0 | Date: 2026-02-17
# ═════════════════════════════════════════════════════════════════════════════

set -e

echo "🏭 OpenClaw Toyota Production System — Installation"
echo "═══════════════════════════════════════════════════════"
echo ""

# Check if we're in the right directory
if [ ! -f "coordination/TPS_OPENCLAW_ARCHITECTURE.md" ]; then
    echo "❌ Error: Run this script from /Users/dhyana/clawd"
    exit 1
fi

echo "📁 Creating directory structure..."

# Create state directory
mkdir -p coordination/state
mkdir -p cells/research/{inputs,wip,outputs,archive}
mkdir -p cells/build/{specs,wip,artifacts}
mkdir -p cells/ship/{queue,wip,released}
mkdir -p logs

echo "✅ Directories created"

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x coordination/*.py

echo "✅ Scripts made executable"

# Create initial state files
echo "📝 Initializing state files..."

cat > coordination/state/research_status.json << 'EOF'
{
  "cell": "research",
  "shakti_mode": "Maheshwari",
  "wip": 0,
  "limit": 3,
  "last_output": null,
  "active_projects": [],
  "quality_gate_passes": 0,
  "quality_gate_fails": 0
}
EOF

cat > coordination/state/build_status.json << 'EOF'
{
  "cell": "build",
  "shakti_mode": "Mahakali",
  "wip": 0,
  "limit": 5,
  "last_output": null,
  "test_failures": 0,
  "failure_duration": 0,
  "last_test_run": null,
  "quality_gate": "unknown"
}
EOF

cat > coordination/state/ship_status.json << 'EOF'
{
  "cell": "ship",
  "shakti_mode": "Mahalakshmi",
  "wip": 0,
  "limit": 2,
  "last_output": null,
  "bootstraps_shipped": [],
  "revenue_pipeline": {},
  "queue_depth": 0
}
EOF

cat > coordination/state/monitor_status.json << 'EOF'
{
  "cell": "monitor",
  "shakti_mode": "Mahasaraswati",
  "wip": 0,
  "limit": 0,
  "last_output": null,
  "metrics_collected": 0
}
EOF

echo "✅ State files initialized"

# Check Python dependencies
echo "🔍 Checking Python dependencies..."

python3 -c "import json; import datetime; import pathlib" 2>/dev/null || {
    echo "⚠️  Warning: Basic Python packages may be missing"
}

echo "✅ Python check complete"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "📋 Installation Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "1. 📖 Read the architecture:"
echo "   cat coordination/TPS_OPENCLAW_ARCHITECTURE.md"
echo ""
echo "2. 🔍 Review the cron schedule:"
echo "   cat coordination/crontab.master"
echo ""
echo "3. ⚡ Install the crontab (BACKUP YOUR CURRENT CRONTAB FIRST):"
echo "   crontab -l > ~/.crontab.backup"
echo "   crontab coordination/crontab.master"
echo ""
echo "4. 🧪 Test individual components:"
echo "   ./coordination/takt_master.py"
echo "   ./coordination/heartbeat_cascade.py"
echo "   ./coordination/cell_research.py"
echo "   ./coordination/cell_build.py"
echo "   ./coordination/cell_ship.py"
echo "   ./coordination/andon_board.py --update"
echo ""
echo "5. 📊 View the Andon board:"
echo "   cat coordination/ANDON_BOARD.md"
echo ""
echo "═══════════════════════════════════════════════════════"
echo "⚠️  IMPORTANT: This system modifies crontab."
echo "   Backup your current crontab before installing!"
echo "═══════════════════════════════════════════════════════"
