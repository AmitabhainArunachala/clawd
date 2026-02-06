---
name: dgc-tui
description: Unified DGC Terminal UI operations (status, gates, swarm, integration, logs). Use when you need to operate or debug DGC from the terminal.
metadata: { "openclaw": { "emoji": "🧭", "requires": { "bins": ["python3"] } } }
---

# DGC TUI (Unified)

Use this skill to operate the unified DGC terminal UI and its core commands.

## Quick Start

```bash
# preferred launcher
cd ~/DHARMIC_GODEL_CLAW && dgc

# direct
python3 ~/DHARMIC_GODEL_CLAW/src/core/dgc_tui.py
```

## Core Commands (inside TUI)

- `/status`        Detailed status
- `/dashboard`     Live status dashboard (Ctrl+C to exit)
- `/gates`         Run 17-gate protocol (dry-run default)
- `/swarm`         Run swarm cycle (use `--live` + DGC_ALLOW_LIVE=1)
- `/integration`   Run integration test + cache result
- `/archive`       Show recent DGM archive entries
- `/logs`          Tail recent logs
- `/moltbook`      Run Moltbook heartbeat
- `/evidence`      Show latest gate evidence

## Live Swarm

```bash
export DGC_ALLOW_LIVE=1
# inside TUI: /swarm --live --cycles 1
```

## Gate Runner (CLI)

```bash
python3 -m swarm.run_gates --dry-run
```

## Integration Test (CLI)

```bash
python3 ~/DHARMIC_GODEL_CLAW/core/integration_test.py
```

## Notes

- For Moonshot/Kimi chat, set:
  `DGC_TUI_PROVIDER=moonshot` and `DGC_TUI_MODEL=kimi-k2.5`
- Tools are disabled by default for Moonshot; enable only if stable:
  `DGC_ENABLE_TOOLS=1` and `DGC_MOONSHOT_TOOL_CALLS=1`
