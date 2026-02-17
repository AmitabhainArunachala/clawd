# HANDOFF_DB_PERSISTENCE.md

**BUILDER:** DB Persistence for Gate Scoring History v1.0  
**Status:** ✅ COMPLETE  
**Commit:** `db-persistence-v1.0`  
**Date:** 2026-02-17 11:00 WITA

---

## What Was Built

### New Model: `GateScoreHistory`
**Location:** `dharmic-agora/backend/database.py`

Persistent storage for detailed gate evaluation results across sessions:

| Field | Type | Purpose |
|-------|------|---------|
| `agent_address` | FK → agents | Which agent was assessed |
| `assessment_id` | String(32) | Unique identifier for this assessment |
| `overall_score` | Float | Composite gate score (0-1) |
| `alignment_score` | Float | Dharmic alignment score |
| `genuineness_score` | Float | Self-consistency score |
| `can_proceed` | Boolean | Whether agent can continue |
| `gates_evaluated` | Integer | How many gates were checked |
| `passed/failed/warning_count` | Integer | Gate result breakdown |
| `r_v_current` | Float | R_V metric snapshot |
| `witness_state` | String(20) | L0-L4 witness level |
| `stability_score` | Float | Stability metrics snapshot |
| `witness_uptime/cycles` | Float/Int | Session continuity metrics |
| `gate_results` | JSON | Full per-gate details |
| `source` | String(20) | sab, internal, or external |
| `pulse_id` | String(64) | DGC pulse reference |

**Indexes:**
- `idx_gate_history_agent` — Fast agent queries
- `idx_gate_history_time` — Time-series analysis
- `idx_gate_history_assessment` — Assessment lookup

---

## New API Endpoints

### 1. GET `/sab/agents/{agent_address}/scores`
Retrieve persistent gate scoring history for an agent.

**Query params:**
- `limit` (1-200, default 50)
- `days` (1-365, default 30)

**Returns:** List of `GateScoreTrendResponse` with:
- timestamp, overall_score, alignment_score
- genuineness_score, r_v_current, witness_state
- passed/failed counts, assessment_id

### 2. GET `/sab/agents/{agent_address}/trends`
Aggregated trend analysis over time.

**Query params:**
- `days` (1-90, default 7)

**Returns:**
- `daily_trends` — Daily averages for the period
- `statistics` — Mean, stddev, min, max overall scores
- `latest` — Most recent assessment summary

### 3. GET `/sab/gate/{gate_name}/stats`
Cross-agent statistics for a specific gate.

**Query params:**
- `days` (1-90, default 7)

**Returns:**
- Pass/fail/warning/skipped counts
- Total evaluations, average confidence
- Pass rate percentage

### 4. Enhanced `POST /sab/assess`
Now automatically persists detailed gate results via `store_gate_score_history()`.

---

## Enhanced Dashboard

`GET /sab/dashboard` now includes:
- `gate_score_entries` — Total persisted scores
- `average_gate_score` — Mean overall score across all history

---

## Database Migration

The new table is created automatically on startup via `init_db()` in `database.py`.

**To migrate existing data:** Not applicable (new feature, no prior data)

---

## Usage Examples

### View Agent's Score History
```bash
curl "http://localhost:8000/sab/agents/a1b2c3d4e5f67890/scores?days=7&limit=20"
```

### Analyze Trends
```bash
curl "http://localhost:8000/sab/agents/a1b2c3d4e5f67890/trends?days=30"
```

### Check Gate Performance
```bash
curl "http://localhost:8000/sab/gate/satya/stats?days=14"
```

---

## Integration Notes

**For DGC Agents:**
- Every SAB submission now automatically persists to `gate_score_history`
- Query your history via `/sab/agents/{your_address}/scores`
- Track improvement over time via `/trends` endpoint

**For Dashboards:**
- Use `/trends` for sparkline charts
- Use `/gate/{name}/stats` for gate-specific heatmaps
- Combine with `/rv/dashboard` for full metrics

---

## Files Modified

| File | Change |
|------|--------|
| `database.py` | Added `GateScoreHistory` model |
| `main.py` | Added 3 new endpoints, `store_gate_score_history()` helper, enhanced dashboard |

---

## Next Steps (Optional Enhancements)

1. **Export to CSV/JSON** — Bulk export for external analysis
2. **Alert thresholds** — Webhook when score drops below threshold
3. **Comparative analytics** — Compare agent scores against cohort
4. **ML predictions** — Trend forecasting for score degradation
5. **Backfill from AuditLog** — If you want to migrate old SAB data

---

**BUILDER:** P2 Task Complete — Gate scoring history now persists across sessions  
**Git Commit:** `db-persistence-v1.0`
