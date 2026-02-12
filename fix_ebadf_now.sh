#!/bin/bash
# OpenClaw EBADF Fix Script
# Run: bash ~/clawd/fix_ebadf_now.sh
# This fixes the 28,533 FD leak and invalid JSON config

set -e

echo "=== OPENCLAW EBADF EMERGENCY FIX ==="
echo "Started: $(date)"
echo ""

# STEP 1: Kill all OpenClaw processes
echo "[1/6] Stopping all OpenClaw processes..."
openclaw gateway stop 2>/dev/null || true
pkill -9 -f openclaw 2>/dev/null || true
pkill -9 -f clawdbot 2>/dev/null || true
pkill -9 -f "node.*18789" 2>/dev/null || true
sleep 5
echo "✓ Processes stopped"
echo ""

# STEP 2: Verify no zombies
echo "[2/6] Checking for zombie processes..."
ZOMBIES=$(ps aux | awk '$8 ~ /^Z/ {print}' | wc -l)
echo "Zombie count: $ZOMBIES"
if [ "$ZOMBIES" -gt 0 ]; then
    echo "⚠️  Zombies found — attempting cleanup..."
    ps aux | awk '$8 ~ /^Z/ {print $2}' | xargs kill -9 2>/dev/null || true
fi
echo ""

# STEP 3: Fix the JSON config
echo "[3/6] Fixing openclaw.json..."
CONFIG="$HOME/.openclaw/openclaw.json"
BACKUP="$HOME/.openclaw/openclaw.json.backup.$(date +%Y%m%d_%H%M%S)"

# Backup
cp "$CONFIG" "$BACKUP"
echo "✓ Backup created: $BACKUP"

# Fix trailing comma issue (common cause of JSON invalid)
# Remove trailing commas before } or ]
python3 << 'EOF'
import json
import sys

config_path = "~/.openclaw/openclaw.json"
config_path = config_path.replace("~", "/Users/dhyana")

try:
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Try to parse
    data = json.loads(content)
    print("✓ JSON is valid")
    
except json.JSONDecodeError as e:
    print(f"⚠️  JSON error at line {e.lineno}: {e.msg}")
    
    # Attempt to fix common issues
    with open(config_path, 'r') as f:
        lines = f.readlines()
    
    # Remove trailing commas before } or ]
    fixed_lines = []
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if stripped.endswith(',') and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line.startswith('}') or next_line.startswith(']'):
                fixed_lines.append(line.rstrip().rstrip(',') + '\n')
                print(f"  Fixed trailing comma at line {i + 1}")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    with open(config_path, 'w') as f:
        f.writelines(fixed_lines)
    
    # Verify fix
    with open(config_path, 'r') as f:
        content = f.read()
    try:
        data = json.loads(content)
        print("✓ JSON fixed and validated")
    except json.JSONDecodeError as e2:
        print(f"✗ JSON still invalid: {e2}")
        sys.exit(1)
EOF

echo ""

# STEP 4: Clean up temp files
echo "[4/6] Cleaning temp files..."
rm -rf /tmp/openclaw-* 2>/dev/null || true
echo "✓ Temp files cleaned"
echo ""

# STEP 5: Increase FD limit and restart
echo "[5/6] Restarting OpenClaw with higher FD limit..."
ulimit -n 65536
echo "✓ FD limit set to 65536"

openclaw gateway start
echo "✓ Gateway started"
sleep 10
echo ""

# STEP 6: Verify
echo "[6/6] Verification..."
echo "--- Gateway status ---"
openclaw gateway status

echo ""
echo "--- FD usage check ---"
OPENCLAW_PID=$(pgrep -f "openclaw-gateway" | head -1)
if [ -n "$OPENCLAW_PID" ]; then
    FD_COUNT=$(lsof -p $OPENCLAW_PID 2>/dev/null | wc -l)
    echo "OpenClaw PID: $OPENCLAW_PID"
    echo "FD count: $FD_COUNT"
    if [ "$FD_COUNT" -lt 500 ]; then
        echo "✓ FD usage healthy (<500)"
    else
        echo "⚠️  FD usage still high: $FD_COUNT"
    fi
else
    echo "✗ OpenClaw not running"
fi

echo ""
echo "--- Port check ---"
netstat -an | grep 18789 | head -5 || echo "No netstat output"

echo ""
echo "=== FIX COMPLETE ==="
echo "Time: $(date)"
echo ""
echo "NEXT STEP: Test DC's exec tool"
echo "Ask DC to run: exec 'date' and see if EBADF is resolved"
echo ""
