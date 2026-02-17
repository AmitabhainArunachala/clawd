# 🏭 OPENCLAW TPS — Quick Reference Card

## System Overview
Toyota Production System adapted for OpenClaw — 4 work cells, 15 staggered cron jobs, zero collision scheduling.

## File Structure
```
coordination/
├── TPS_OPENCLAW_ARCHITECTURE.md  # Full architecture document
├── crontab.master                # 15-job schedule
├── install.sh                    # Installation script
│
├── takt_master.py                # 1-minute heartbeat (Job 1)
├── heartbeat_cascade.py          # 15-min sync (Job 9)
│
├── cell_research.py              # Research cell (Job 8)
├── cell_build.py                 # Build cell (Job 4)
├── cell_ship.py                  # Ship cell (Job 5)
│
├── andon_board.py                # Escalation board (Job 10)
├── wake_sync.py                  # Morning brief (Job 14)
├── night_brief.py                # Evening review (Job 15)
└── kaizen_review.py              # Weekly PDCA (Weekly)

cells/
├── research/{inputs,wip,outputs,archive}
├── build/{specs,wip,artifacts}
└── ship/{queue,wip,released}

state/
└── *.json                        # Cell status files
```

## Quick Commands

### Test Components
```bash
# Test takt master
./coordination/takt_master.py

# Test heartbeat cascade
./coordination/heartbeat_cascade.py

# Test cells
./coordination/cell_research.py
./coordination/cell_build.py
./coordination/cell_ship.py

# Update andon board
./coordination/andon_board.py --update

# Pull emergency cord
./coordination/andon_board.py --pull "Critical failure" --cell build

# Reset cord
./coordination/andon_board.py --reset
```

### View Status
```bash
# Andon board (visual status)
cat coordination/ANDON_BOARD.md

# Pipeline status
cat PIPELINE_STATUS.md

# Morning brief
cat MORNING_BRIEF.md

# Evening brief
cat EVENING_BRIEF.md

# Kaizen review
cat KAIZEN_WEEKLY.md
```

### Monitor Logs
```bash
# Takt log
tail -f logs/takt.log

# Heartbeat log
tail -f logs/heartbeat.log

# Cell logs
tail -f logs/{research,build,ship}.log

# Escalation log
tail -f logs/escalation.log
```

## Work Cells

| Cell | Shakti Mode | WIP Limit | Takt Time | Purpose |
|------|-------------|-----------|-----------|---------|
| Research | Maheshwari | 3 | 15 min | R_V, AIKAGRYA, arXiv |
| Build | Mahakali | 5 | 5 min | DGC, WITNESS, CI |
| Ship | Mahalakshmi | 2 | 5 min | Bootstraps, revenue |
| Monitor | Mahasaraswati | ∞ | 5 min | Health, metrics |

## Cron Schedule (15 Jobs)

| # | Job | Schedule | Offset | Purpose |
|---|-----|----------|--------|---------|
| 1 | Takt Master | Every minute | 0 | System heartbeat |
| 2 | MMK Poll | Every 5 min | 0 | Agent status |
| 3 | TRISHULA Router | Every 5 min | 1 min | Message routing |
| 4 | Build Cell | Every 5 min | 2 min | CI/CD pulse |
| 5 | Ship Cell | Every 5 min | 3 min | Release check |
| 6 | Alert Check | Every 10 min | 2 min | Escalation eval |
| 7 | Dashboard | Every 10 min | 5 min | Visual status |
| 8 | Research Cell | Every 15 min | 0 | arXiv/insights |
| 9 | OpenClaw Beat | Every 15 min | 7 min | Cascade sync |
| 10 | Andon Board | Hourly +5 min | 5 min | Escalation board |
| 11 | Pipeline Esc | Hourly +10 min | 10 min | Stale item escalation |
| 12 | TRISHULA Review | Hourly | 0 | Accountability |
| 13 | VPS Sync | Every 4 hours | 0 | Remote sync |
| 14 | Wake Sync | Daily 06:00 WITA | 0 | Morning brief |
| 15 | Night Brief | Daily 21:00 WITA | 0 | Evening review |

## Quality Gates

### Research Gate
- ✅ Source cited
- ✅ Insight actionable
- ✅ Not duplicate

### Build Gate
- ✅ Tests passing
- ✅ Type checking clean
- ✅ Security scan clear

### Ship Gate
- ✅ Legal reviewed
- ✅ Pricing verified
- ✅ Assets ready
- ✅ Support docs

## Andon Escalation

| Level | Trigger | Action |
|-------|---------|--------|
| 🟢 Green | Normal | Continue |
| 🟡 Yellow | Stale >1hr | Notify, auto-fix |
| 🔴 Red | Stale >4hr | Stop cell, escalate |
| 🚨 Cord | Emergency | All-hands stop |

## Poka-Yoke (Mistake-Proofing)

- **Handoff Validation**: Required fields checked
- **Duplicate Detection**: Content hash comparison
- **WIP Limits**: Hard stops at max capacity
- **Auto-Save**: State saved every pulse
- **Atomic Writes**: Temp file + rename pattern

## Kaizen (Continuous Improvement)

**Weekly PDCA Cycle:**
1. **Plan**: Review metrics, identify bottlenecks
2. **Do**: Implement one change
3. **Check**: Measure for 7 days
4. **Act**: Standardize or abandon

**Metrics Tracked:**
- Gate success rate
- Shipment velocity
- Escalation rate
- Flow efficiency

## Troubleshooting

### No cascade signal
```bash
# Check takt master
ls -la coordination/state/cascade_signal.json
cat coordination/state/cascade_signal.json
```

### Cell not updating
```bash
# Check cell state
cat coordination/state/{cell}_status.json

# Run manually to see errors
./coordination/cell_{name}.py
```

### Andon showing wrong status
```bash
# Force update
./coordination/andon_board.py --update
cat coordination/ANDON_BOARD.md
```

## Integration Points

| System | Integration | Latency Target |
|--------|-------------|----------------|
| MMK | Agent polling | 5 min |
| TRISHULA | Message routing | 1 min |
| OpenClaw | Work dispatch | 15 min |
| VPS | State sync | 4 hours |

## Success Metrics

| Target | Current | Goal |
|--------|---------|------|
| Latency | 2 hours | <30 seconds |
| Bootstraps | 0 | 6 in 30 days |
| Revenue | $0 | $1,000 (month 1) |
| Gate Pass | — | >90% |

---

*Reference Version: 1.0*  
*For full details: TPS_OPENCLAW_ARCHITECTURE.md*
