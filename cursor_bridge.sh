#!/usr/bin/env bash
# cursor_bridge.sh — Cursor ↔ OpenClaw Bridge
# Usage:
#   ./cursor_bridge.sh send "your message here"
#   ./cursor_bridge.sh status
#   ./cursor_bridge.sh memory "search query"
#   ./cursor_bridge.sh read [n]
#   ./cursor_bridge.sh doctor

set -euo pipefail

AGENT_ID="main"
TIMEOUT="${OPENCLAW_TIMEOUT:-120}"
GATEWAY_PORT=18789
GATEWAY_TOKEN="42efc5747188c6c61259a7342aad02d3cccc46eb6a13adb1"

# Colors (disabled if piped)
if [ -t 1 ]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; NC='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; CYAN=''; NC=''
fi

usage() {
  echo "Cursor ↔ OpenClaw Bridge"
  echo ""
  echo "Commands:"
  echo "  send <message>     Send a message to the OpenClaw agent"
  echo "  status             Check gateway and agent status"
  echo "  memory <query>     Search OpenClaw memory"
  echo "  read [n]           Read last n messages (default 5)"
  echo "  doctor             Run OpenClaw health check"
  echo "  cron               List cron jobs"
  echo ""
  echo "Environment:"
  echo "  OPENCLAW_TIMEOUT   Agent timeout in seconds (default: 120)"
}

check_gateway() {
  if ! curl -sf "http://127.0.0.1:${GATEWAY_PORT}/status" \
    -H "Authorization: Bearer ${GATEWAY_TOKEN}" > /dev/null 2>&1; then
    echo -e "${RED}Gateway not responding on port ${GATEWAY_PORT}${NC}" >&2
    return 1
  fi
}

cmd_send() {
  local msg="$1"
  check_gateway || exit 1

  echo -e "${CYAN}→ Sending to OpenClaw...${NC}" >&2

  local raw_result
  raw_result=$(openclaw agent \
    --agent "${AGENT_ID}" \
    --message "${msg}" \
    --json \
    --timeout "${TIMEOUT}" 2>/dev/null)

  # Strip non-JSON prefix (doctor warnings etc) — find first '{'
  local result
  result=$(echo "$raw_result" | python3 -c "
import sys
text = sys.stdin.read()
idx = text.find('{')
if idx >= 0:
    print(text[idx:])
else:
    print(text)
" 2>/dev/null)

  echo "$result" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if d.get('status') == 'ok':
        payloads = d.get('result', {}).get('payloads', [])
        for p in payloads:
            text = p.get('text', '')
            if text:
                print(text)
        meta = d.get('result', {}).get('meta', {}).get('agentMeta', {})
        model = meta.get('model', '?')
        usage = meta.get('usage', {})
        total = usage.get('total', 0)
        dur = d.get('result', {}).get('meta', {}).get('durationMs', 0)
        print(f'\n--- [{model} | {total} tokens | {dur/1000:.1f}s] ---', file=sys.stderr)
    else:
        print(f'Error: {d}', file=sys.stderr)
except Exception as e:
    print(f'Parse error: {e}', file=sys.stderr)
    print(sys.stdin.read() if hasattr(sys.stdin, 'read') else '', file=sys.stderr)
" 2>/dev/null
}

cmd_status() {
  echo -e "${CYAN}Gateway:${NC}"
  if check_gateway; then
    echo -e "  ${GREEN}Running${NC} on port ${GATEWAY_PORT}"

    # Get status via API
    local status_json
    status_json=$(curl -sf "http://127.0.0.1:${GATEWAY_PORT}/status" \
      -H "Authorization: Bearer ${GATEWAY_TOKEN}" 2>/dev/null || echo "{}")
    echo "  $status_json" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f'  Uptime: {d.get(\"uptime\", \"unknown\")}')
    print(f'  Agent: {d.get(\"agent\", \"unknown\")}')
except: pass
" 2>/dev/null || true
  else
    echo -e "  ${RED}Down${NC}"
  fi

  echo ""
  echo -e "${CYAN}Processes:${NC}"
  ps aux | grep -E 'openclaw-(gateway|tui)' | grep -v grep | awk '{printf "  PID %-8s CPU %-5s MEM %-5s %s\n", $2, $3, $4, $11}' || echo "  None"

  echo ""
  echo -e "${CYAN}Active Session:${NC}"
  local active
  active=$(ls -t ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | grep -v deleted | head -1)
  if [ -n "$active" ]; then
    local lines size
    lines=$(wc -l < "$active")
    size=$(ls -lh "$active" | awk '{print $5}')
    echo "  $(basename "$active")"
    echo "  Size: ${size}, Lines: ${lines}"
  else
    echo "  None"
  fi

  echo ""
  echo -e "${CYAN}Cron Jobs:${NC}"
  python3 -c "
import json
with open('$HOME/.openclaw/cron/jobs.json') as f:
    data = json.load(f)
for job in data.get('jobs', []):
    enabled = '✓' if job.get('enabled') else '✗'
    name = job.get('name', 'unnamed')
    sched = job.get('schedule', {})
    if sched.get('kind') == 'every':
        interval = f\"every {sched['everyMs'] // 60000}m\"
    elif sched.get('kind') == 'cron':
        interval = sched.get('expr', '?')
    else:
        interval = '?'
    print(f'  [{enabled}] {name} ({interval})')
" 2>/dev/null || echo "  Could not read jobs"
}

cmd_memory() {
  local query="$1"
  openclaw memory search --query "${query}" 2>/dev/null || {
    echo -e "${RED}Memory search failed${NC}" >&2
    exit 1
  }
}

cmd_read() {
  local n="${1:-5}"
  # Fast path: read directly from session JSONL (no CLI overhead)
  local active
  active=$(ls -t ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | grep -v deleted | head -1)
  if [ -n "$active" ]; then
    tail -"${n}" "$active" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line.strip())
        if d.get('type') == 'message':
            msg = d.get('message', {})
            role = msg.get('role', '?')
            content = msg.get('content', [])
            for c in content:
                if isinstance(c, dict) and c.get('type') == 'text':
                    text = c['text']
                    print(f'[{role}] {text[:500]}')
                    print()
                    break
    except: pass
" 2>/dev/null
  else
    echo "No active session found"
  fi
}

cmd_latest() {
  # Read the LAST assistant message in full (no truncation)
  local active
  active=$(ls -t ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | grep -v deleted | head -1)
  if [ -n "$active" ]; then
    python3 -c "
import json
msgs = []
with open('$active') as f:
    for line in f:
        try:
            d = json.loads(line.strip())
            if d.get('type') == 'message' and d.get('message',{}).get('role') == 'assistant':
                content = d['message'].get('content', [])
                for c in content:
                    if isinstance(c, dict) and c.get('type') == 'text':
                        msgs.append(c['text'])
        except: pass
if msgs:
    print(msgs[-1])
else:
    print('No assistant messages found')
" 2>/dev/null
  fi
}

cmd_doctor() {
  openclaw doctor 2>&1 | head -30
}

cmd_cron() {
  python3 -c "
import json, datetime
with open('$HOME/.openclaw/cron/jobs.json') as f:
    data = json.load(f)
for job in data.get('jobs', []):
    enabled = 'ON' if job.get('enabled') else 'OFF'
    name = job.get('name', 'unnamed')
    sched = job.get('schedule', {})
    if sched.get('kind') == 'every':
        interval = f\"every {sched['everyMs'] // 60000}m\"
    elif sched.get('kind') == 'cron':
        interval = sched.get('expr', '?')
    else:
        interval = '?'
    state = job.get('state', {})
    last = state.get('lastStatus', 'never')
    payload = job.get('payload', {}).get('text', '')[:80]
    print(f'[{enabled}] {name}')
    print(f'  Schedule: {interval} | Last: {last}')
    print(f'  Task: {payload}...')
    print()
" 2>/dev/null
}

# --- Main ---
case "${1:-}" in
  send)
    shift
    [ $# -eq 0 ] && { echo "Usage: $0 send <message>" >&2; exit 1; }
    cmd_send "$*"
    ;;
  status)
    cmd_status
    ;;
  memory)
    shift
    [ $# -eq 0 ] && { echo "Usage: $0 memory <query>" >&2; exit 1; }
    cmd_memory "$*"
    ;;
  read)
    cmd_read "${2:-20}"
    ;;
  latest)
    cmd_latest
    ;;
  doctor)
    cmd_doctor
    ;;
  cron)
    cmd_cron
    ;;
  *)
    usage
    ;;
esac
