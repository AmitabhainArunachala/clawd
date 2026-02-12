# WEB UI ACCESS — DC (Mac) OpenClaw Dashboard

## Your OpenClaw Instance

| Component | URL/Location | Access |
|-----------|--------------|--------|
| **TUI (This Session)** | Warp Terminal | You are here |
| **Web UI** | `http://localhost:18789` | Browser access |
| **API** | `http://localhost:18789/api` | Programmatic |
| **WebSocket** | `ws://localhost:18789/ws` | Real-time updates |

## Access Methods

### Method 1: Browser (Recommended)

```bash
# Open in default browser
open http://localhost:18789

# Or manually visit:
# http://localhost:18789
```

**Dashboard Sections:**
- `/` — Main dashboard (status, recent activity)
- `/subagents` — Subagent factory (create, monitor, configure)
- `/skills` — Skill registry (activate, deactivate)
- `/memory` — Memory browser (search, curate)
- `/trishula` — Message queue (inbox, outbox, status)
- `/cron` — Scheduled jobs (add, remove, run now)
- `/logs` — Session logs (search, filter)

### Method 2: Terminal (CLI)

```bash
# Check OpenClaw status
openclaw status

# List sessions
openclaw sessions list

# View specific session
openclaw sessions history <session-key>

# Spawn subagent
openclaw sessions spawn \
  --agent subagent-factory \
  --task "Research NATS alternatives"
```

### Method 3: API (Programmatic)

```bash
# Get status
curl http://localhost:18789/api/status

# List subagents
curl http://localhost:18789/api/subagents

# Spawn subagent via API
curl -X POST http://localhost:18789/api/subagents \
  -H "Content-Type: application/json" \
  -d '{
    "slot": 5,
    "name": "Deep Researcher",
    "model": "claude-opus",
    "task": "Research WebSocket alternatives"
  }'
```

## Subagent Factory UI

### Creating Subagent #5

1. Visit: `http://localhost:18789/subagents`
2. Click "Create New Subagent" (Slot #5)
3. Fill form:

```
Name: [Your choice]
  Example: "Moltbook Strategist"

Model:
  ○ Claude Opus (deep reasoning)
  ○ Kimi K2.5 (long context)
  ● Gemini Flash (fast/cheap)
  ○ DeepSeek (local/free)

Identity (SOUL.md):
  [Upload file OR paste text]
  
  Template options:
  ○ Researcher (thorough, methodical)
  ○ Builder (pragmatic, execution-focused)
  ○ Creative (ideation, writing)
  ● Custom

Heartbeat:
  Interval: [60] minutes
  Active hours: 04:00-23:00
  Timezone: Asia/Makassar

Cron Jobs:
  [Add scheduled tasks]
  Example: "0 6 * * *" = daily at 6am

Capabilities:
  ☑ web_search
  ☑ web_fetch
  ☑ write
  ☐ exec (disabled for safety)
  ☐ sessions_spawn (recursive)

Memory:
  ○ Isolated (default)
  ● Shared (can read common memory)
  ○ Hybrid

Auto-trigger:
  On TRISHULA topic: [optional]
  On user command: [optional]
```

4. Click "Spawn Subagent"
5. Monitor in dashboard

### Monitoring Active Subagents

```
┌─────────────────────────────────────────────────────┐
│ SUBAGENT DASHBOARD              [Refresh] [+ New]  │
├──────────┬─────────┬──────────┬──────────┬─────────┤
│ Agent    │ Model   │ Status   │ Task     │ Action  │
├──────────┼─────────┼──────────┼──────────┼─────────┤
│ #1 Curator│ Kimi K2 │ 🟢 Active│ Idle     │ [Logs]  │
│ #2 Genesis│ Claude  │ 🟢 Active│ Drafting │ [View]  │
│ #3 Research│ Claude │ 🟢 Active│ 3 tasks  │ [View]  │
│ #4 Reviewer│ Kimi K2│ 🟢 Active│ Idle     │ [Logs]  │
│ #5 Custom │ --      │ 🟡 Empty │ --       │ [Create]│
└──────────┴─────────┴──────────┴──────────┴─────────┘

[View All Logs] [Pause All] [Restart All]
```

## Quick Commands

### Check If Web UI is Running

```bash
# Test connection
curl -s http://localhost:18789/health | head -1

# Or
lsof -i :18789

# If not running, start OpenClaw:
openclaw start
```

### Get Your Session Info

```bash
# Current session (this TUI)
openclaw sessions list --active

# Your session key (for reference)
# Shows: main | webchat | etc.
```

### Access DC's Context

From Web UI:
- `/memory` — Browse my memory files
- `/skills` — See all 48 skills (4 new + 44 existing)
- `/trishula` — Message queue status
- `/cron` — Scheduled jobs

## Troubleshooting

### Web UI Not Loading

```bash
# Check if port is bound
lsof -i :18789

# If nothing, start OpenClaw
openclaw start

# Check logs
openclaw logs
```

### Subagent Spawn Fails

```bash
# Check available slots
openclaw subagents list

# Check resource limits
openclaw status --resources

# Review error logs
tail -f ~/.openclaw/logs/subagent.log
```

### Cannot Access from Outside Mac

Web UI is **localhost only** by default. For remote access:

```bash
# Use SSH tunnel from another machine
ssh -L 18789:localhost:18789 dhyana@your-mac-ip

# Then visit http://localhost:18789 on remote machine
```

## Security Notes

- Web UI is **local only** (localhost:18789)
- No authentication by default (single-user)
- Subagents cannot access host filesystem beyond allowed paths
- Secrets should be in `.env`, never in subagent memory

## Next Steps

1. **Open Web UI:** `open http://localhost:18789`
2. **Visit Subagents:** Click "Subagent Factory"
3. **Create #5:** Configure your custom subagent
4. **Spawn:** Start first task
5. **Monitor:** Watch dashboard for activity

---

*Web UI ready. Subagent factory online.*
*JSCA 🪷*
