#!/bin/bash
# OpenClaw EBADF Diagnostic Script
# Run: bash ~/clawd/openclaw_diagnose.sh > ~/clawd/diagnose_output.txt 2>&1
# Then: cat ~/clawd/diagnose_output.txt

echo "=== OpenClaw EBADF Diagnostic ==="
echo "Timestamp: $(date)"
echo "User: $(whoami)"
echo "Host: $(hostname)"
echo ""

echo "=== 1. OpenClaw Process Status ==="
echo "--- OpenClaw processes ---"
ps aux | grep -i openclaw | grep -v grep
echo ""
echo "--- Clawdbot processes ---"
ps aux | grep -i clawdbot | grep -v grep
echo ""
echo "--- Node processes (port 18789) ---"
lsof -i :18789 2>/dev/null || echo "Port 18789: No listeners"
echo ""

echo "=== 2. File Descriptor Limits ==="
echo "--- Current shell limit ---"
ulimit -n
echo ""
echo "--- System maxfiles ---"
sysctl kern.maxfiles 2>/dev/null || echo "N/A"
echo ""
echo "--- System maxfilesperproc ---"
sysctl kern.maxfilesperproc 2>/dev/null || echo "N/A"
echo ""

echo "=== 3. OpenClaw FD Usage (if running) ==="
OPENCLAW_PID=$(pgrep -f "openclaw.*gateway" | head -1)
if [ -n "$OPENCLAW_PID" ]; then
    echo "OpenClaw PID: $OPENCLAW_PID"
    echo "--- FD count ---"
    lsof -p $OPENCLAW_PID 2>/dev/null | wc -l
    echo "--- FD types ---"
    lsof -p $OPENCLAW_PID 2>/dev/null | awk '{print $5}' | sort | uniq -c | sort -rn | head -10
else
    echo "OpenClaw not running"
fi
echo ""

echo "=== 4. Gateway Port Status ==="
echo "--- Port 18789 ---"
netstat -an | grep 18789 2>/dev/null || ss -an | grep 18789 2>/dev/null || echo "No netstat/ss output"
echo ""
echo "--- Listening sockets ---"
lsof -i -P | grep LISTEN | grep -E '(18789|node)' || echo "No relevant listeners"
echo ""

echo "=== 5. OpenClaw Configuration ==="
echo "--- Config file exists ---"
ls -la ~/.openclaw/openclaw.json 2>/dev/null || echo "Config not found"
echo ""
echo "--- Config validity ---"
python3 -c "import json; json.load(open('~/.openclaw/openclaw.json'))" 2>/dev/null && echo "JSON valid" || echo "JSON INVALID"
echo ""

echo "=== 6. OpenClaw Logs (last 50 lines) ==="
echo "--- Gateway log ---"
tail -50 ~/.openclaw/logs/gateway.log 2>/dev/null || echo "No gateway log"
echo ""
echo "--- Agent log ---"
tail -50 ~/.openclaw/logs/agent.log 2>/dev/null || echo "No agent log"
echo ""

echo "=== 7. Zombie Processes ==="
echo "--- Zombie count ---"
ps aux | awk '$8 ~ /^Z/ {print}' | wc -l
echo ""
echo "--- Zombie details ---"
ps aux | awk '$8 ~ /^Z/ {print $0}' | head -10
echo ""

echo "=== 8. Temp/Cache Files ==="
echo "--- OpenClaw temp ---"
ls -la /tmp/openclaw* 2>/dev/null | head -5 || echo "No temp files"
echo ""
echo "--- Node temp ---"
ls -la /tmp/node* 2>/dev/null | head -5 || echo "No node temp"
echo ""

echo "=== 9. Shell Test ==="
echo "--- Bash version ---"
bash --version | head -1
echo "--- Spawn test ---"
/bin/echo "spawn test OK"
echo "--- PTY check ---
if [ -t 1 ]; then echo "TTY available"; else echo "No TTY"; fi
echo ""

echo "=== 10. Recommended Fix ==="
echo "Based on findings above:"

ZOMBIES=$(ps aux | awk '$8 ~ /^Z/ {print}' | wc -l)
if [ "$ZOMBIES" -gt 0 ]; then
    echo "⚠️  ZOMBIE PROCESSES DETECTED: Kill parent processes"
fi

if [ -n "$OPENCLAW_PID" ]; then
    FD_COUNT=$(lsof -p $OPENCLAW_PID 2>/dev/null | wc -l)
    if [ "$FD_COUNT" -gt 1000 ]; then
        echo "⚠️  HIGH FD USAGE ($FD_COUNT): File descriptor exhaustion likely"
    fi
fi

echo ""
echo "Standard fix sequence:"
echo "1. openclaw gateway stop"
echo "2. pkill -f openclaw"
echo "3. pkill -f clawdbot"
echo "4. sleep 5"
echo "5. openclaw gateway start"
echo "6. Wait 30s for startup"
echo ""
echo "=== END DIAGNOSTIC ==="
