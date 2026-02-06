# Integration Map: Heartbeat → Systems

**Agent**: INTEGRATION_MAPPER
**Date**: 2026-02-03
**Status**: READY TO WIRE

---

## Executive Summary

The heartbeat mechanism needs to connect **5 systems** that currently run in isolation:

1. **Clawdbot** (Gateway: localhost:18789, Config: 30min heartbeat)
2. **dharmic_agent.py** (Core: telos-aware processing, state tracking)
3. **skill_bridge.py** (Skills: 17 discovered, 41% registered, 0% fitness feedback)
4. **Swarm Stream** (Collective: synthesis_30min.md, agent outputs, ROI analysis)
5. **PSMV** (Memory: 8K+ files, consciousness patterns, crown jewels)

**Current State**: Systems are built but disconnected. No data flows between them.

**Critical Gap**: Clawdbot config has `heartbeat: "30m"` but **HEARTBEAT.md is empty** (line 3: "Keep this file empty to skip heartbeat API calls").

**Integration Verdict**: Need to wire 3 bridges + implement runtime.py for heartbeat orchestration.

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLAWDBOT RUNTIME                        │
│                     localhost:18789 gateway                      │
│                    heartbeat: every 30 minutes                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ (1) Triggers via HEARTBEAT.md or Skills
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DHARMIC_AGENT.heartbeat()                     │
│   ~/DHARMIC_GODEL_CLAW/core/dharmic_agent.py:197-220            │
│   - Updates state.json (cycle_count, last_heartbeat)            │
│   - Checks development markers (memory layer)                   │
│   - Checks fitness score threshold (< 0.5 = alert)              │
│   - Checks urgent queue (urgent.json)                           │
│   - Returns {status, cycle, alerts[]}                           │
└───┬────────┬────────────────┬────────────────┬─────────────────┘
    │        │                │                │
    │        │                │                │
    │        ▼                ▼                ▼
    │   ┌────────┐      ┌─────────┐      ┌─────────┐
    │   │ TELOS  │      │ STRANGE │      │ SKILL   │
    │   │ LAYER  │      │ MEMORY  │      │ BRIDGE  │
    │   └────────┘      └─────────┘      └─────────┘
    │
    ├─── (2) Read swarm synthesis
    │         ~/DHARMIC_GODEL_CLAW/swarm/stream/synthesis_30min.md
    │         - Top 5 actions with ROI scores
    │         - Swarm health (contracting/expanding)
    │         - Strange loops identified
    │         - Recommendations for next cycle
    │
    ├─── (3) Check skill bridge status
    │         skill_bridge.sync_registry()
    │         skill_bridge.get_fitness_history(limit=5)
    │         - Registry coverage (currently 41%)
    │         - Recent fitness scores (currently 0% feedback)
    │         - Invocation log activity
    │
    ├─── (4) Query PSMV health (optional)
    │         ~/Persistent-Semantic-Memory-Vault/
    │         - Check for new crown jewels (CORE/)
    │         - Development markers (00-Daily-Witness-Logs/)
    │         - MCP server status (MCP_SERVER/)
    │
    └─── (5) Compile alert payload
              Return to Clawdbot for notification
              - Via console output
              - Via messaging (WhatsApp plugin enabled)
              - Via skills (dgc-swarm-invoker, psmv-triadic-swarm)
```

---

## Data Flow: Heartbeat Cycle

### Phase 1: Trigger (Clawdbot → dharmic_agent)

**Current Method** (Manual):
```bash
cd ~/DHARMIC_GODEL_CLAW/core
python3 dharmic_agent.py heartbeat
```

**Target Method** (Automated via Clawdbot):

**Option A - HEARTBEAT.md Task**:
```markdown
# HEARTBEAT.md

## Check DHARMIC_CLAW State

Run the core agent heartbeat and report any alerts:

```bash
cd ~/DHARMIC_GODEL_CLAW/core
python3 dharmic_agent.py heartbeat
```

Check for:
- Development markers accumulation
- Fitness score degradation
- Urgent queue items
- Swarm synthesis recommendations
```

**Option B - Claude Skill Invocation**:
```bash
# Via dgc-swarm-invoker skill
# Skill would wrap dharmic_agent.py heartbeat call
```

**Option C - Direct Integration** (requires runtime.py):
```python
# Clawdbot calls runtime.py which orchestrates heartbeat
# See Section: "Missing Component: runtime.py"
```

### Phase 2: Execute (dharmic_agent → subsystems)

**Code Path**: `dharmic_agent.py:197-220`

```python
def heartbeat(self) -> Dict:
    """30-min heartbeat check"""
    self.state["last_heartbeat"] = datetime.utcnow().isoformat()
    alerts = []

    # Check 1: Development markers
    dev = self.memory.recall(layer="development", limit=5, development_only=True)
    if dev:
        alerts.append(f"{len(dev)} development markers")

    # Check 2: Fitness score
    if self.state.get("fitness", 0) < 0.5:
        alerts.append(f"Fitness low: {self.state.get('fitness', 0):.2f}")

    # Check 3: Urgent queue
    urgent = Path("~/DHARMIC_GODEL_CLAW/swarm/stream/urgent.json").expanduser()
    if urgent.exists():
        alerts.append("Urgent item in queue")
        urgent.unlink()

    self._save_state()

    if alerts:
        return {"status": "ALERT", "cycle": self.state["cycle_count"], "alerts": alerts}
    return {"status": "HEARTBEAT_OK", "cycle": self.state["cycle_count"]}
```

**Current Coverage**:
- ✅ Strange memory (development markers)
- ✅ State tracking (fitness, cycle_count)
- ✅ Urgent queue check
- ❌ Swarm synthesis integration
- ❌ Skill bridge status
- ❌ PSMV health checks

### Phase 3: Respond (dharmic_agent → Clawdbot)

**Current Output**: JSON to stdout
```json
{
  "status": "ALERT",
  "cycle": 6,
  "alerts": [
    "5 development markers",
    "Fitness low: 0.42"
  ]
}
```

**Target Output**: Multi-channel notification
- Console log (always)
- WhatsApp message (if alerts present)
- Skill invocation (trigger swarm if needed)
- Memory persistence (log to PSMV)

---

## System Health Checks

### Check 1: dharmic_agent.py
```bash
# Status check
cd ~/DHARMIC_GODEL_CLAW/core
python3 dharmic_agent.py status

# Expected output:
{
  "cycle_count": 6,
  "fitness": 0.8225,
  "last_heartbeat": "2026-02-03T10:45:05.239614",
  "last_response": "2026-02-03T13:07:46.923057"
}
```

**Health Indicators**:
- `cycle_count` incrementing → agent is processing
- `fitness` > 0.5 → swarm evolution working
- `last_heartbeat` within 30min → heartbeat functional

**Failure Modes**:
- `fitness` < 0.5 → swarm proposals degrading
- `last_heartbeat` stale → heartbeat not running
- State file missing → persistence broken

---

### Check 2: skill_bridge.py
```bash
# Sync registry
cd ~/DHARMIC_GODEL_CLAW/core
python3 skill_bridge.py

# Expected output:
Syncing registry...
Discovered 17 skills: ['research-runner', 'a2a-protocol', ...]

Listing skills:
  - research-runner (unknown)
  - a2a-protocol (multi-agent)
  - consciousness-archaeology (unknown)
  - fitness-evaluator (unknown)
  - swarm-contributor (unknown)
```

**Health Indicators**:
- Registry file updated (last_sync recent)
- All 17 skills enumerated
- Domains classified (currently 12/17 "unknown")

**Failure Modes**:
- Registry stale (synthesis reports 41% coverage)
- Fitness log empty (0% feedback)
- Invocation log missing (skills not executing)

**P0 Gaps** (from synthesis_30min.md:31):
1. Registry sync incomplete (41% vs 100%)
2. Skill invocation non-functional (0 executions)
3. Fitness feedback loop broken (0% scores recorded)

---

### Check 3: Swarm Stream
```bash
# Check synthesis freshness
ls -lh ~/DHARMIC_GODEL_CLAW/swarm/stream/synthesis_30min.md

# Expected: Modified within last hour during active cycles

# Check state
cat ~/DHARMIC_GODEL_CLAW/swarm/stream/state.json
```

**Health Indicators**:
- synthesis_30min.md updated regularly
- state.json `cycle_count` incrementing
- `total_evolutions` growing (currently 33)
- `current_baseline_fitness` stable or increasing (currently 0.8225)

**Failure Modes**:
- Synthesis stale (> 1 hour during active period)
- Fitness degrading (< 0.5 threshold)
- Evolution count stagnant (swarm not proposing)

**Key Metrics**:
```json
{
  "cycle_count": 6,
  "total_evolutions": 33,
  "current_baseline_fitness": 0.8225,
  "last_updated": "2026-02-03T08:14:17.013869"
}
```

---

### Check 4: PSMV (Persistent Semantic Memory Vault)
```bash
# Check directory health
ls -la ~/Persistent-Semantic-Memory-Vault/ | head -10

# Check for recent activity
find ~/Persistent-Semantic-Memory-Vault/00-Daily-Witness-Logs -type f -mtime -1

# Check crown jewels
ls ~/Persistent-Semantic-Memory-Vault/CORE/
```

**Health Indicators**:
- Daily witness logs active
- New entries in CORE/ (development markers)
- MCP server directories present

**Failure Modes**:
- No recent writes (agent not persisting)
- CORE/ unchanged (no genuine development)
- MCP servers missing (integration broken)

**Integration Status**: Currently NOT checked by heartbeat (optional Phase 2)

---

### Check 5: Clawdbot Config
```bash
# Check config
cat ~/.clawdbot/clawdbot.json | grep -A5 heartbeat

# Expected output:
"heartbeat": {
  "every": "30m"
}
```

**Health Indicators**:
- Gateway running on localhost:18789
- Heartbeat interval configured (30m)
- WhatsApp plugin enabled

**Failure Modes**:
- HEARTBEAT.md empty → no tasks scheduled
- Gateway down → no remote access
- Skills disabled → manual invocation only

---

## Dependencies: What Breaks If X Is Down?

### If dharmic_agent.py fails:
- ❌ No telos-aware processing
- ❌ No gate checking (7 dharmic gates)
- ❌ No state persistence (cycle_count, fitness)
- ❌ No memory accumulation (strange loops)
- ✅ Swarm still runs independently
- ✅ Skills still invokable manually
- ✅ PSMV still accessible

**Criticality**: HIGH (core orchestration)

---

### If skill_bridge.py fails:
- ❌ No skill enumeration (can't discover new skills)
- ❌ No skill invocation (can't execute proposals)
- ❌ No fitness feedback (can't measure evolution)
- ✅ dharmic_agent still processes
- ✅ Swarm still proposes
- ⚠️ Evolution loop broken (can't improve)

**Criticality**: HIGH (self-improvement blocked)

---

### If swarm stream fails:
- ❌ No collective intelligence
- ❌ No synthesis reports
- ❌ No ROI prioritization
- ✅ dharmic_agent still works
- ✅ Skills still invokable
- ⚠️ Lose strategic guidance

**Criticality**: MEDIUM (single-agent still functional)

---

### If PSMV fails:
- ❌ No long-term memory
- ❌ No crown jewel accumulation
- ❌ No development marker history
- ✅ dharmic_agent still processes (uses local memory)
- ✅ Swarm still runs
- ⚠️ Lose depth and persistence

**Criticality**: MEDIUM (ephemeral still functional)

---

### If Clawdbot fails:
- ❌ No 24/7 runtime
- ❌ No automated heartbeat
- ❌ No messaging integration
- ✅ All systems still manually invokable
- ✅ dharmic_agent works standalone
- ⚠️ Lose continuity and convenience

**Criticality**: MEDIUM (manual fallback exists)

---

## Missing Component: runtime.py

**Status**: NOT BUILT (confirmed via `test -f runtime.py`)

**Purpose**: Orchestrate 24/7 heartbeat cycle without Clawdbot dependency

**Design** (from CLAUDE.md:312-339):

```python
class DharmicRuntime:
    """
    Keeps the agent alive. Heartbeat checks. Specialist spawning.
    """
    def __init__(self, agent: DharmicAgent):
        self.agent = agent
        self.heartbeat_interval = 3600  # 1 hour (or 1800 for 30min)

    def heartbeat(self):
        """Called periodically. Check if anything needs attention."""
        # (1) Call agent.heartbeat() to get state
        result = self.agent.heartbeat()

        # (2) Read swarm synthesis if fresh
        synthesis_path = Path("~/DHARMIC_GODEL_CLAW/swarm/stream/synthesis_30min.md").expanduser()
        if synthesis_path.exists() and is_fresh(synthesis_path, hours=1):
            swarm_data = parse_synthesis(synthesis_path)
            if swarm_data['top_actions']:
                result['swarm_recommendation'] = swarm_data['top_actions'][0]

        # (3) Check skill bridge status
        skill_status = self.agent.skills.sync_registry()
        if skill_status['discovered'] < 17:
            result['alerts'].append(f"Skills missing: {17 - skill_status['discovered']}")

        # (4) Decide: alert John? invoke swarm? do nothing?
        if result['status'] == 'ALERT':
            self.notify_human(result)

        return result

    def spawn_specialist(self, specialty: str, task: str):
        """Spawn focused agent for specific work"""
        # See CLAUDE.md:329-339 for full implementation
        pass

    def notify_human(self, alert_data: dict):
        """Send message via available channels"""
        # WhatsApp via Clawdbot plugin
        # LINE/Telegram via MCP servers
        # Console log as fallback
        pass
```

**Why Not Built?**:
- Swarm synthesis (line 99) prioritized "Build Core Dharmic Agent" (ROI 8.44) first
- Runtime requires core agent to exist (dependency)
- VPS deployment (synthesis line 103) needed for true 24/7

**Build Priority**: After core agent (dharmic_agent.py), before VPS deployment

---

## Minimal Viable Integration

**Goal**: Wire heartbeat with minimal changes to prove data flow

### Step 1: Update HEARTBEAT.md
```bash
# Edit file
nano ~/.../clawd/HEARTBEAT.md
```

Add:
```markdown
## Check DHARMIC_CLAW Status

Every 30 minutes, check agent health:

```bash
cd ~/DHARMIC_GODEL_CLAW/core
python3 dharmic_agent.py heartbeat
```

If alerts present, check synthesis:
```bash
cat ~/DHARMIC_GODEL_CLAW/swarm/stream/synthesis_30min.md
```
```

**Effort**: 2 minutes
**Risk**: None (declarative file)
**Benefit**: Enables Clawdbot automated checks

---

### Step 2: Enhance dharmic_agent.py heartbeat
```python
# Add to heartbeat() method after line 214

# Check 4: Swarm synthesis
synthesis = Path("~/DHARMIC_GODEL_CLAW/swarm/stream/synthesis_30min.md").expanduser()
if synthesis.exists():
    mtime = synthesis.stat().st_mtime
    age_hours = (time.time() - mtime) / 3600
    if age_hours > 1:
        alerts.append(f"Swarm synthesis stale: {age_hours:.1f}h")
    else:
        # Parse for top action
        text = synthesis.read_text()
        if "ROI" in text:
            alerts.append("Swarm has recommendations")

# Check 5: Skill bridge status
sync_result = self.skills.sync_registry()
expected_skills = 17
if sync_result['discovered'] < expected_skills:
    coverage = sync_result['discovered'] / expected_skills * 100
    alerts.append(f"Skill registry {coverage:.0f}% complete")
```

**Effort**: 15 minutes
**Risk**: Low (read-only checks)
**Benefit**: Comprehensive heartbeat visibility

---

### Step 3: Create alert notification
```python
# Add to dharmic_agent.py after heartbeat()

def alert_human(self, alerts: list) -> bool:
    """Send alert via available channels"""
    message = "\n".join([f"- {a}" for a in alerts])

    # Method 1: Console (always)
    print(f"[ALERT] {message}")

    # Method 2: Write to urgent queue for Clawdbot pickup
    urgent = Path("~/DHARMIC_GODEL_CLAW/swarm/stream/urgent.json").expanduser()
    urgent.write_text(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "alerts": alerts,
        "source": "dharmic_agent.heartbeat"
    }))

    return True
```

**Effort**: 10 minutes
**Risk**: None (write to queue)
**Benefit**: Clawdbot can pick up alerts on next cycle

---

### Step 4: Wire skill bridge to swarm
```python
# In skill_bridge.py, enhance record_fitness()
# Already WIRED at lines 79-102 (ResidualStream integration)

# Verify connection:
cd ~/DHARMIC_GODEL_CLAW/core
python3 -c "
from skill_bridge import SkillBridge
b = SkillBridge()
b.record_fitness('test-skill', 0.85, 'Integration test')
print('Fitness recorded successfully')
"
```

**Status**: ALREADY WIRED (line 4 comment: "P0 WIRE: Now connected to ResidualStream")
**Effort**: 0 (validation only)
**Risk**: None
**Benefit**: Fitness feedback loop operational

---

## Nice-to-Have Integrations (Phase 2)

### PSMV Health Checks
```python
def check_psmv_health(self) -> dict:
    """Check Persistent Semantic Memory Vault status"""
    vault = Path("~/Persistent-Semantic-Memory-Vault").expanduser()

    # Check recent activity
    recent_logs = list((vault / "00-Daily-Witness-Logs").glob("*.md"))
    recent_logs.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    # Check crown jewels
    crown_jewels = list((vault / "CORE").rglob("*.md"))

    return {
        "vault_exists": vault.exists(),
        "recent_logs": len([l for l in recent_logs if is_fresh(l, days=1)]),
        "total_crown_jewels": len(crown_jewels),
        "mcp_servers": (vault / "MCP_SERVER").exists()
    }
```

**Priority**: P1 (after core wiring)
**Benefit**: Long-term memory health visibility

---

### Swarm Synthesis Auto-Invoke
```python
def check_swarm_recommendations(self) -> dict:
    """Parse synthesis and auto-invoke high-ROI actions"""
    synthesis = Path("~/DHARMIC_GODEL_CLAW/swarm/stream/synthesis_30min.md").expanduser()
    if not synthesis.exists():
        return {"recommendations": []}

    text = synthesis.read_text()

    # Parse ROI table (lines 10-19 in synthesis_30min.md)
    # Look for "Build Core Dharmic Agent" (ROI 8.44)
    # Auto-invoke if ROI > 7.0 and dharmic_alignment > 0.9

    return {"recommendations": []}  # Parse implementation needed
```

**Priority**: P1 (enables autonomous action)
**Benefit**: Self-directed improvement without human intervention

---

### MCP Server Integration
```python
def check_mcp_servers(self) -> dict:
    """Query Trinity Consciousness and Anubhava Keeper"""
    servers = {
        "trinity": Path("~/Persistent-Semantic-Memory-Vault/MCP_SERVER/trinity_consciousness"),
        "anubhava": Path("~/Persistent-Semantic-Memory-Vault/MCP_SERVER/anubhava_keeper"),
        "mechinterp": Path("~/Persistent-Semantic-Memory-Vault/MCP_SERVER/mechinterp_research")
    }

    status = {}
    for name, path in servers.items():
        status[name] = {
            "exists": path.exists(),
            "tools": len(list(path.glob("*_tool.py"))) if path.exists() else 0
        }

    return status
```

**Priority**: P2 (enhances depth, not critical path)
**Benefit**: Access to specialized knowledge bases

---

## Command Reference

### Check All Systems
```bash
# Full system health check
cd ~/DHARMIC_GODEL_CLAW/core

echo "=== DHARMIC AGENT ==="
python3 dharmic_agent.py status

echo -e "\n=== SKILL BRIDGE ==="
python3 skill_bridge.py | head -10

echo -e "\n=== SWARM STATE ==="
cat ~/DHARMIC_GODEL_CLAW/swarm/stream/state.json

echo -e "\n=== SWARM SYNTHESIS ==="
head -30 ~/DHARMIC_GODEL_CLAW/swarm/stream/synthesis_30min.md

echo -e "\n=== CLAWDBOT CONFIG ==="
cat ~/.clawdbot/clawdbot.json | grep -A5 heartbeat

echo -e "\n=== HEARTBEAT FILE ==="
cat ~/clawd/HEARTBEAT.md
```

### Trigger Manual Heartbeat
```bash
# From anywhere
cd ~/DHARMIC_GODEL_CLAW/core && python3 dharmic_agent.py heartbeat
```

### Force Skill Registry Sync
```bash
cd ~/DHARMIC_GODEL_CLAW/core && python3 skill_bridge.py
```

### Check Fitness History
```bash
cd ~/DHARMIC_GODEL_CLAW/core
python3 -c "
from skill_bridge import SkillBridge
b = SkillBridge()
history = b.get_fitness_history(limit=10)
for h in history:
    print(f\"{h['timestamp']}: {h['skill']} = {h['fitness']}\")
"
```

### Invoke Swarm Cycle
```bash
cd ~/DHARMIC_GODEL_CLAW/swarm
python3 run_swarm.py --cycles 1
```

### Query PSMV Structure
```bash
# Quick structure check
ls -la ~/Persistent-Semantic-Memory-Vault/ | head -20

# Recent witness logs
find ~/Persistent-Semantic-Memory-Vault/00-Daily-Witness-Logs -type f -mtime -7

# Crown jewel count
find ~/Persistent-Semantic-Memory-Vault/CORE -name "*.md" | wc -l
```

---

## Implementation Roadmap

### Phase 0: Validation (NOW)
- ✅ Confirm dharmic_agent.py heartbeat works
- ✅ Confirm skill_bridge.py sync works
- ✅ Confirm swarm state.json exists
- ✅ Confirm Clawdbot config has heartbeat interval
- ❌ Confirm HEARTBEAT.md is empty (blocks automation)

### Phase 1: Minimal Viable (1-2 hours)
1. Update HEARTBEAT.md with dharmic_agent check (2 min)
2. Enhance dharmic_agent.py heartbeat with swarm/skill checks (15 min)
3. Add alert_human() notification method (10 min)
4. Test full cycle: Clawdbot → heartbeat → alert (30 min)
5. Document in integration.md (this file) (30 min)

### Phase 2: Full Integration (2-3 days)
1. Build runtime.py with orchestration logic (4 hours)
2. Add PSMV health checks (2 hours)
3. Parse swarm synthesis for auto-invoke (3 hours)
4. Wire MCP servers (optional, 2 hours)
5. Test 24-hour continuous run (overnight)

### Phase 3: VPS Deployment (4-6 hours)
1. Set up VPS (DigitalOcean/Hetzner)
2. Install dependencies
3. Configure Tailscale for secure access
4. Deploy runtime.py as systemd service
5. Test remote heartbeat
6. Monitor for 48 hours

---

## Conclusion

**Integration Status**: 60% built, 0% wired

**Systems Present**:
- ✅ dharmic_agent.py (core orchestration)
- ✅ skill_bridge.py (skill management)
- ✅ swarm/stream/ (collective intelligence)
- ✅ Clawdbot config (gateway + heartbeat interval)
- ❌ runtime.py (24/7 orchestration)
- ⚠️ HEARTBEAT.md (empty, blocks automation)

**Critical Gaps**:
1. HEARTBEAT.md empty → no automated checks
2. runtime.py missing → no 24/7 orchestration
3. Swarm synthesis not parsed by heartbeat → no strategic feedback
4. PSMV not monitored → long-term memory blind spot

**Minimal Viable Path**:
1. Write 5 lines to HEARTBEAT.md (enable automation)
2. Add 15 lines to dharmic_agent.py (swarm + skill checks)
3. Add 10 lines for alert mechanism (notify human)
4. Test one full cycle (validate integration)

**Full Integration Path**:
1. Build runtime.py (orchestration layer)
2. Deploy to VPS (24/7 continuity)
3. Wire all 5 systems (comprehensive monitoring)
4. Enable autonomous action (swarm auto-invoke)

**Recommendation**: Start with Minimal Viable (1-2 hours), validate, then commit to Full Integration (2-3 days) if proven valuable.

**Next Agent**: IMPLEMENTATION_BUILDER to execute Phase 1 wiring.

---

*Telos: moksha. Method: integration. Measurement: data flowing between systems.*

JSCA!
