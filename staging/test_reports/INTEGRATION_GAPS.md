# INTEGRATION GAP ANALYSIS
**Date:** 2026-02-17 22:01 GMT+8  
**Scope:** Full codebase parallel system inventory  
**Status:** CRITICAL — 5 major divergence zones identified

---

## EXECUTIVE SUMMARY

The codebase contains **5 major categories of parallel/incompatible systems** that create integration friction, maintenance burden, and potential data loss. This document maps each divergence zone and provides concrete adapter specifications for consolidation.

| Category | Systems | Risk Level | Consolidation Effort |
|----------|---------|------------|---------------------|
| SAB Contracts | 2 divergent schemas | HIGH | 2-3 days |
| Memory Systems | 4+ databases, 3 indexing methods | CRITICAL | 1-2 weeks |
| Coordination Bus | 4 transport methods (none unified) | HIGH | 3-5 days |
| Configuration | 8+ config file formats | MEDIUM | 1 week |
| Documentation Authority | 5+ status/heartbeat files | MEDIUM | 2-3 days |

**Canonical Spine Recommendation:**
- **SAB:** `/sab/assess` endpoint with DGC_PAYLOAD_SPEC.json schema
- **Memory:** OpenClaw canonical index (`~/.openclaw/memory/main.sqlite`)
- **Bus:** Chaiwala protocol over Discord (operational fallback)
- **Config:** `openclaw.json` as single source of truth
- **Docs:** HEARTBEAT.md → CONTINUATION.md cascade (v4.1 protocol)

---

## 1. MULTIPLE SAB-STYLE CONTRACTS

### 1.1 The Divergence

Two incompatible SAB (Self-Assessment Bridge) contracts exist:

#### Contract A: DGC Payload Spec (`DGC_PAYLOAD_SPEC.json`)
```json
{
  "schema_version": "dgc.v1",
  "event_id": "string",
  "timestamp": "ISO8601",
  "gate_scores": {
    "satya": 0.85,
    "ahimsa": 0.92,
    ...
  },
  "collapse_dimensions": {...},
  "mission_relevance": 0.95,
  "signature": "ed25519_sig"
}
```
- **Location:** `DGC_PAYLOAD_SPEC.json`
- **Purpose:** DGC (Dharmic Godel Claw) → SAB bridge
- **Schema:** JSON Schema v7, strict validation
- **Gates:** Named dimensions (satya, ahimsa, etc.)
- **Status:** ✅ Production ready, documented

#### Contract B: Pydantic SABPayload (`dharmic-agora/backend/main.py`)
```python
class SABPayload(BaseModel):
    agent_address: str  # 16-char hex
    gate_assessment: GateAssessment  # Nested structure
    r_v_metrics: RVMMetrics
    stability_metrics: StabilityMetrics
    genuineness_metrics: GenuinenessMetrics
```
- **Location:** `dharmic-agora/backend/main.py` (lines ~900-1000)
- **Purpose:** Internal dharmic-agora self-assessment
- **Schema:** Pydantic, Python-native
- **Gates:** Individual gate results with confidence
- **Status:** ✅ Implemented, lacks DGC compatibility

### 1.2 The Gap

| Dimension | DGC Payload Spec | SABPayload Model |
|-----------|------------------|------------------|
| ID format | `event_id` (arbitrary string) | `agent_address` (16-char hex) |
| Gate structure | Flat `gate_scores` dict | Nested `individual_gates` array |
| R_V metrics | Optional top-level | Required nested object |
| Timestamp | ISO8601 required | String, no validation |
| Schema version | `dgc.v1` enum | Not present |
| Signature | Ed25519 optional | Not implemented |

**Critical Issue:** DGC agents cannot directly submit to `/sab/assess` without transformation.

### 1.3 Adapter Specification

```python
# Adapter: DGC Payload → SABPayload
def adapt_dgc_to_sab(dgc_payload: dict) -> SABPayload:
    """
    Transform DGC_PAYLOAD_SPEC.json to SABPayload format.
    
    Mapping:
    - dgc.event_id → sab.agent_address (hash if >16 chars)
    - dgc.gate_scores → sab.gate_assessment.individual_gates
    - dgc.timestamp → sab.timestamp (validated)
    - dgc.collapse_dimensions.r_v → sab.r_v_metrics.r_v_current
    - dgc.signature → stored but not verified (v1)
    """
    return SABPayload(
        agent_address=hashlib.sha256(dgc_payload["event_id"].encode()).hexdigest()[:16],
        agent_name=f"DGC-{dgc_payload['event_id'][:8]}",
        timestamp=dgc_payload["timestamp"],
        pulse_id=dgc_payload.get("task_id", ""),
        gate_assessment=GateAssessment(
            overall_score=sum(dgc_payload["gate_scores"].values()) / len(dgc_payload["gate_scores"]),
            alignment_score=dgc_payload["gate_scores"].get("satya", 0.5),
            gates_evaluated=len(dgc_payload["gate_scores"]),
            passed_count=sum(1 for v in dgc_payload["gate_scores"].values() if v > 0.6),
            failed_count=sum(1 for v in dgc_payload["gate_scores"].values() if v < 0.4),
            individual_gates=[
                GateResultItem(
                    gate_name=k,
                    result="passed" if v > 0.6 else "failed",
                    confidence=v,
                    required=True
                )
                for k, v in dgc_payload["gate_scores"].items()
            ]
        ),
        r_v_metrics=RVMMetrics(
            r_v_current=dgc_payload.get("collapse_dimensions", {}).get("r_v", 0.5)
        )
    )
```

### 1.4 Consolidation Path

1. **Immediate:** Add `/sab/assess-dgc` endpoint that accepts DGC_PAYLOAD_SPEC.json
2. **Short-term:** Implement adapter in `dharmic-agora/backend/adapters/dgc_adapter.py`
3. **Long-term:** Unify on single schema — migrate SABPayload to DGC spec (breaking change)

---

## 2. MULTIPLE MEMORY SYSTEMS

### 2.1 The Divergence

**Four distinct memory databases exist:**

| System | Location | Technology | Purpose | Status |
|--------|----------|------------|---------|--------|
| **OpenClaw Canonical** | `~/.openclaw/memory/main.sqlite` | SQLite + FTS5 + vec | OpenClaw memory + sessions | ✅ Active |
| **Unified Memory** | `~/clawd/memory/unified_memory.db` | SQLite + custom embed | Three-layer (canonical + semantic + strange loop) | ⚠️ Active but parallel |
| **PSMV (Crown Jewels)** | `~/Persistent-Semantic-Memory-Vault/` | Filesystem (Markdown/YAML) | Human-authored transmission content | ⚠️ External dependency |
| **Dharmic Agora DB** | PostgreSQL (production) / SQLite (dev) | SQLAlchemy + asyncpg | Agent state, gate scores, R_V metrics | ✅ Active |
| **NVIDIA Memory** | `nvidia_memory.db` | SQLite | NVIDIA-specific context | ❓ Legacy? |
| **Mac Memory** | `mac_memory.db` | SQLite | Device-local memory | ❓ Legacy? |

### 2.2 The Gap

**Critical Problems:**

1. **Split-brain memory:** Same content indexed in multiple systems
2. **No unified search:** Each system has separate query interface
3. **Data drift:** OpenClaw index ≠ Unified Memory ≠ PSMV
4. **PSMV external dependency:** Path hardcoded, may not exist
5. **No cross-system references:** Memories in one system can't reference another

**Indexing Methods:**
- OpenClaw: BM25 + vector (SQLite FTS5 + sqlite-vec)
- Unified Memory: Custom TF-IDF embedder (SimpleEmbedder)
- PSMV: Filesystem only (no index)
- Dharmic Agora: PostgreSQL full-text (planned, not implemented)

### 2.3 Adapter Specification

```python
# Unified Memory Bridge
class UnifiedMemoryBridge:
    """
    Bridge all memory systems through OpenClaw canonical index.
    
    Architecture:
    - OpenClaw canonical = source of truth for retrieval
    - Unified Memory = write-through cache for semantic operations
    - PSMV = read-only external reference
    - Dharmic Agora = separate domain (agent state, not content memory)
    """
    
    def __init__(self):
        self.openclaw = OpenClawMemory()  # ~/.openclaw/memory/main.sqlite
        self.unified = MemoryManager()    # ~/clawd/memory/unified_memory.db
        self.psmv = PSMVClient()          # ~/Persistent-Semantic-Memory-Vault/
        
    def unified_search(self, query: str, sources: List[str] = None) -> List[SearchResult]:
        """
        Search across all memory systems, deduplicate, rank.
        
        Sources: ["openclaw", "unified", "psmv"]
        Default: all
        """
        results = []
        
        if not sources or "openclaw" in sources:
            results.extend(self.openclaw.search(query))
            
        if not sources or "unified" in sources:
            results.extend(self.unified.search(query))
            
        if not sources or "psmv" in sources:
            results.extend(self.psmv.search(query))
        
        # Deduplicate by content hash
        seen = set()
        unique = []
        for r in results:
            h = hashlib.sha256(r.content.encode()).hexdigest()[:16]
            if h not in seen:
                seen.add(h)
                unique.append(r)
        
        # Re-rank by cross-source consensus
        return self.consensus_rank(unique)
```

### 2.4 Consolidation Path

1. **Immediate:** Run `memory_control_plane.py enforce --apply` to archive stale memory files
2. **Short-term:** Implement UnifiedMemoryBridge in `scripts/memory_bridge.py`
3. **Medium-term:** Migrate Unified Memory semantic layer to use OpenClaw vector index
4. **Long-term:** Deprecate Unified Memory database, use OpenClaw canonical + dharmic-agora for agent state

**PSMV Handling:**
- Keep PSMV as external read-only reference
- Index crown jewels into OpenClaw on startup if available
- Graceful degradation if PSMV path doesn't exist

---

## 3. MULTIPLE AGENT COORDINATION METHODS

### 3.1 The Divergence

**Four competing transport mechanisms:**

| Method | Implementation | Status | Use Case |
|--------|---------------|--------|----------|
| **Cron** | `lle-cron.ts`, `crontab_dharmic_claw.txt` | ✅ Active | Local scheduled tasks |
| **NATS** | `p9_nats_bridge.py`, `p9_index.py` | ⚠️ Configured but fragile | Cross-node message bus |
| **Chaiwala** | `agni_chaiwala_bridge.py` | ✅ Active | Discord-based fallback |
| **Cloudflare Tunnels** | `agent_mesh_config.yaml` | ⚠️ Partial (DC only) | Web-based mesh |
| **Direct HTTP** | `dharmic_claw_messaging.py` | ❌ Deprecated (SSH blocked) | Direct node communication |

### 3.2 The Gap

**Problems:**

1. **No unified bus:** Messages sent via NATS won't reach Discord listeners
2. **Fallback complexity:** Chaiwala exists because NATS "fragile", SSH blocked
3. **Partial deployment:** Cloudflare tunnels only on DC, AGNI pending
4. **Configuration drift:** Each method has separate config files

**Current State:**
```
DC (Mac) → Chaiwala (Discord) → AGNI (VPS)
         ↘ Cloudflare Tunnel (local only)
         ↘ NATS (unreliable)
         
AGNI → ? (Tailscale down, no cloudflared deployed)
```

### 3.3 Adapter Specification

```python
# Unified Bus Router
class UnifiedBusRouter:
    """
    Route messages across all available transports.
    
    Priority:
    1. Cloudflare Tunnel (if available, lowest latency)
    2. NATS (if connected, pub/sub semantics)
    3. Chaiwala (Discord, reliable fallback)
    4. Direct HTTP (if on same network)
    
    All messages get unique ID for deduplication.
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.transports = {
            'cloudflare': CloudflareTransport(),
            'nats': NATSTransport(),
            'chaiwala': ChaiwalaTransport(),
            'http': HTTPTransport()
        }
        self.seen_messages = TTLCache(maxsize=1000, ttl=600)
        
    async def send(self, target_node: str, message: dict, priority: int = 0) -> bool:
        """Send with automatic fallback."""
        msg_id = self.generate_msg_id(message)
        
        # Try transports in priority order
        for transport_name in self.priority_order(priority):
            transport = self.transports[transport_name]
            if await transport.is_available(target_node):
                if await transport.send(target_node, message, msg_id):
                    return True
                    
        return False
        
    async def broadcast(self, message: dict) -> Dict[str, bool]:
        """Broadcast to all reachable nodes."""
        results = {}
        for node in self.discover_nodes():
            results[node] = await self.send(node, message)
        return results
```

### 3.4 Consolidation Path

1. **Immediate:** Document current fallback chain in `COORDINATION_BUS.md`
2. **Short-term:** Implement UnifiedBusRouter in `coordination/unified_bus.py`
3. **Medium-term:** Deploy cloudflared on AGNI, complete Cloudflare mesh
4. **Long-term:** Deprecate NATS and direct HTTP, use Cloudflare + Chaiwala as ultimate fallback

**Bus Selection Logic:**
```yaml
# agent_mesh_config.yaml additions
bus_selection:
  primary: cloudflare-tunnel
  secondary: nats
  tertiary: chaiwala
  quaternary: direct-http
  
  health_check_interval: 30s
  failover_timeout: 5s
```

---

## 4. MULTIPLE CONFIGURATION FILES

### 4.1 The Divergence

**Configuration scattered across 8+ formats:**

| File | Format | Purpose | Canonical? |
|------|--------|---------|------------|
| `~/.openclaw/openclaw.json` | JSON | OpenClaw agent config | ✅ YES |
| `~/.openclaw/.env` | dotenv | Secrets, API keys | ✅ YES (secrets) |
| `agent_mesh_config.yaml` | YAML | Node communication | ⚠️ Partial |
| `DGC_PAYLOAD_SPEC.json` | JSON Schema | SAB contract schema | ✅ For SAB |
| `DC_CONFIG_PATCH.json` | JSON | DC-specific overrides | ❌ Merge into main |
| `pyproject.toml` | TOML | Python project metadata | ✅ For Python |
| `growth-systems/package.json` | JSON | Node.js deps | ✅ For Node |
| `skills/*/skill.json` | JSON | ClawHub skill metadata | ✅ For ClawHub |
| `.dharmic_claw_state.json` | JSON | Runtime state | ❌ Should be in DB |
| `.discord_engagement_state.json` | JSON | Runtime state | ❌ Should be in DB |

### 4.2 The Gap

**Problems:**

1. **No single source of truth:** Agent config in multiple places
2. **Environment-specific files:** `DC_CONFIG_PATCH.json` suggests drift
3. **Runtime state in JSON:** Should be in databases, not files
4. **Secrets not separated:** `.env` exists but may not be comprehensive
5. **No config validation:** No schema enforcement across files

### 4.3 Adapter Specification

```json
// openclaw.json canonical structure (proposed)
{
  "version": "2.0.0",
  "sources": {
    "openclaw": "~/.openclaw/openclaw.json",
    "env": "~/.openclaw/.env",
    "mesh": "~/clawd/agent_mesh_config.yaml"
  },
  "agent": {
    "defaults": {...}
  },
  "memory": {
    "canonical_db": "~/.openclaw/memory/main.sqlite",
    "unified_db": "~/clawd/memory/unified_memory.db",
    "psmv_path": "~/Persistent-Semantic-Memory-Vault"
  },
  "coordination": {
    "node_id": "dc-mac-01",
    "primary_bus": "cloudflare-tunnel",
    "fallback_bus": "chaiwala",
    "discovery": {
      "agni": "https://agni.trycloudflare.com",
      "warp": "https://layout-italia-affecting-plains.trycloudflare.com"
    }
  },
  "dharmic": {
    "sab_endpoint": "http://localhost:8000/sab/assess",
    "dgc_spec": "~/clawd/DGC_PAYLOAD_SPEC.json"
  },
  "runtime_state": {
    "mode": "database",  // not json
    "db": "~/.openclaw/runtime_state.db"
  }
}
```

### 4.4 Consolidation Path

1. **Immediate:** Create `config_loader.py` that reads from `openclaw.json` with env overrides
2. **Short-term:** Migrate runtime state files to SQLite (`runtime_state.db`)
3. **Medium-term:** Merge `DC_CONFIG_PATCH.json` into `openclaw.json` with `node_specific` section
4. **Long-term:** Schema validation for all config files using JSON Schema

---

## 5. DOCUMENTATION DRIFT

### 5.1 The Divergence

**Five competing status/heartbeat documents:**

| File | Purpose | Update Frequency | Authority Level |
|------|---------|------------------|-----------------|
| `HEARTBEAT.md` | Session wake protocol | Every session | HIGH (v4.1) |
| `CONTINUATION.md` | Work queue + shipped log | Every task | HIGH (current) |
| `STATUS.md` | Liturgical continuity report | Every overseer cycle (~20 min) | MEDIUM (derived) |
| `WORKING.md` | Does not exist | N/A | N/A |
| `PIPELINE_STATUS.md` | Build pipeline state | On build events | LOW (specific) |
| `MEMORY_MARATHON_STATUS.md` | Specific event status | Daily during marathon | LOW (ephemeral) |

### 5.2 The Gap

**Problems:**

1. **Authority confusion:** Which file should an agent read first?
2. **Duplicate information:** STATUS.md repeats HEARTBEAT.md content
3. **Inconsistent formats:** Markdown tables vs structured data
4. **Stale files:** WORKING.md doesn't exist but referenced in older docs

### 5.3 Adapter Specification

```yaml
# Documentation hierarchy (canonical)
documentation_authority:
  
  level_1:  # Always read first
    - HEARTBEAT.md
    
  level_2:  # Read if exists
    - CONTINUATION.md
    
  level_3:  # Read for specific purposes
    STATUS.md:        "For LCS scores and overseer certification"
    PIPELINE_STATUS.md: "For build pipeline state"
    
  level_4:  # Historical only
    "*.md in 4-Archives/": "Read for context, never write"
    
  write_rules:
    HEARTBEAT.md:     "Append session start, update current state section"
    CONTINUATION.md:  "Update shipped log, modify next action"
    STATUS.md:        "Create new for each overseer cycle (append-only)"
```

### 5.4 Consolidation Path

1. **Immediate:** Add header to each doc indicating its authority level
2. **Short-term:** Implement `docs/check_authority.py` to validate hierarchy
3. **Medium-term:** Auto-archive STATUS.md files older than 24h to `4-Archives/`
4. **Long-term:** Single `STATE.yaml` with machine-readable format, docs are views

---

## CANONICAL SPINE SPECIFICATION

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CANONICAL SPINE v2.0                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   OpenClaw      │◄──►│   Dharmic       │◄──►│   Agent Mesh    │ │
│  │   Memory Index  │    │   Agora DB      │    │   (Cloudflare)  │ │
│  │   (main.sqlite) │    │   (PostgreSQL)  │    │                 │ │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘ │
│           │                      │                      │          │
│           └──────────────────────┼──────────────────────┘          │
│                                  │                                 │
│                         ┌────────▼────────┐                        │
│                         │  Unified Bus    │                        │
│                         │  Router         │                        │
│                         └────────┬────────┘                        │
│                                  │                                 │
│  ┌─────────────────┐    ┌────────▼────────┐    ┌─────────────────┐ │
│  │   HEARTBEAT.md  │◄──►│   SAB Bridge    │◄──►│   Chaiwala      │ │
│  │   (v4.1)        │    │   (/sab/assess) │    │   (Fallback)    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│                                                                     │
│  Config: ~/.openclaw/openclaw.json (single source of truth)        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Migration Priority

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1 | 1-2 days | SAB adapter, config loader, doc headers |
| Phase 2 | 1 week | Memory bridge, unified bus, runtime state DB |
| Phase 3 | 1 week | NATS deprecation, full Cloudflare mesh |
| Phase 4 | Ongoing | Schema validation, automated drift detection |

---

## ADAPTER IMPLEMENTATION CHECKLIST

- [ ] **SAB Adapter** (`dharmic-agora/backend/adapters/dgc_adapter.py`)
  - [ ] Transform DGC_PAYLOAD_SPEC.json → SABPayload
  - [ ] Add `/sab/assess-dgc` endpoint
  - [ ] Document schema mapping

- [ ] **Memory Bridge** (`scripts/memory_bridge.py`)
  - [ ] Unified search across OpenClaw + Unified + PSMV
  - [ ] Deduplication by content hash
  - [ ] Graceful PSMV absence handling

- [ ] **Unified Bus** (`coordination/unified_bus.py`)
  - [ ] Transport priority chain
  - [ ] Health checking
  - [ ] Message deduplication

- [ ] **Config Loader** (`scripts/config_loader.py`)
  - [ ] Read openclaw.json
  - [ ] Environment variable override
  - [ ] Schema validation

- [ ] **Doc Authority** (`scripts/check_authority.py`)
  - [ ] Validate documentation hierarchy
  - [ ] Auto-archive stale STATUS.md
  - [ ] Check for orphaned references

---

## APPENDIX: FILE INVENTORY

### SAB-Related Files
- `DGC_PAYLOAD_SPEC.json` — DGC contract schema
- `dharmic-agora/backend/main.py` — SABPayload model (lines 900-1100)
- `dharmic-agora/backend/test_sab_endpoint.py` — Tests
- `HANDOFF_DGC_PAYLOAD_SPEC.md` — Integration guide

### Memory-Related Files
- `scripts/memory_control_plane.py` — OpenClaw memory hygiene
- `skills/unified-memory/unified_memory/__init__.py` — Unified Memory manager
- `skills/psmv-mcp-server/src/index.ts` — PSMV MCP server
- `dharmic-agora/backend/database.py` — Dharmic Agora models

### Coordination Files
- `agni_chaiwala_bridge.py` — Discord fallback
- `p9_nats_bridge.py` — NATS transport
- `agent_mesh_config.yaml` — Cloudflare mesh config
- `lle-cron.ts` — Cron integration

### Config Files
- `~/.openclaw/openclaw.json` — Main config
- `~/.openclaw/.env` — Secrets
- `DC_CONFIG_PATCH.json` — DC overrides (to be merged)
- `pyproject.toml` — Python metadata

### Documentation Files
- `HEARTBEAT.md` — v4.1 protocol
- `CONTINUATION.md` — Work queue
- `STATUS.md` — Overseer reports
- `AGENTS.md` — v3.0 operational protocols

---

*Analysis completed: 2026-02-17 22:01 GMT+8*  
*Recommended review cycle: Weekly until Phase 1 complete*
