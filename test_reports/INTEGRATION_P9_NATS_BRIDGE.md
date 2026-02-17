# INTEGRATION_P9_NATS_BRIDGE.md
**Bridge:** P9 Indexer ↔ NATS Message Bus  
**Status:** ✅ OPERATIONAL (Mac), ⏳ PENDING (AGNI)  
**Path:** `~/clawd/p9_nats_bridge.py`  
**Last Verified:** 2026-02-17

---

## Purpose
Exposes P9 semantic memory via NATS request-reply protocol. Enables cross-node memory queries: any node can search another node's indexed documents.

## Cross-System Compatibility

### Local (Mac - DC)
| Component | Status | Notes |
|-----------|--------|-------|
| P9 Indexer | ✅ 1,386 docs | `p9_index.py`, `p9_search.py` |
| NATS Bridge | ✅ Running | `p9_nats_bridge.py` |
| NATS Server | ✅ Connected | Local/remote NATS |
| Search Latency | ~8ms | BM25 + hybrid ranking |

### Remote (AGNI - VPS)
| Component | Status | Notes |
|-----------|--------|-------|
| P9 Indexer | ✅ 19K docs | Canonical memory |
| NATS Bridge | ⏳ Pending | Awaiting activation |
| Connection | ⚠️ Tailscale down | Blocking AGNI access |

### Remote (RUSHABDEV - VPS)
| Component | Status | Notes |
|-----------|--------|-------|
| Files | ~2K | SAB codebase |
| P9/NATS | ❌ Not started | Awaiting setup |

## API Surface

### NATS Request Format
```json
{
  "query": "R_V metric validation",
  "top_k": 5,
  "hybrid": true
}
```

### NATS Response Format
```json
{
  "results": [
    {
      "path": "~/clawd/.../PHASE1_FINAL_REPORT.md",
      "score": 0.94,
      "snippet": "R_V < 1.0 during recursive..."
    }
  ],
  "latency_ms": 8,
  "index_size": 1386
}
```

### CLI Usage
```bash
# Start bridge
python p9_nats_bridge.py --db mac_memory.db --nats nats://localhost:4222

# Query from any node
nats request dc.memory.search '{"query":"consciousness measurement"}'
```

## Integration Points

1. **Three-World Mesh**: DC ↔ AGNI ↔ RUSHABDEV memory federation
2. **Kaizen OS**: JIKOKU spans indexed and searchable
3. **UPSTREAMS v0**: 30 dependencies now queryable
4. **KEYSTONES 72H**: 12 P0 items tracked via YAML frontmatter
5. **49-Node Indra's Net**: Bidirectional link resolution

## Network Topology

```
┌─────────────┐     NATS      ┌─────────────┐
│   DC (Mac)  │◄─────────────►│  AGNI (VPS) │
│  • 1K docs  │   (Tailscale) │  • 19K docs │
│  • PSMV     │               │  • Factory  │
└─────────────┘               └─────────────┘
       │                            │
       └────────────┬───────────────┘
                    │
              ┌─────────────┐
              │RUSHAB (VPS) │  ◄── Pending
              │  • 2K files │
              └─────────────┘
```

## Test Coverage
- Unit: ✅ P9 search core tested
- Integration: ✅ NATS request-reply tested locally
- Cross-node: ⚠️ Blocked (Tailscale down)
- Load: ⚠️ Not stress tested

## Known Limitations
1. **Tailscale down**: AGNI unreachable since 2026-02-10
2. **No auth**: NATS connection unauthenticated (local only)
3. **Single-threaded**: Bridge handles one query at a time
4. **No replication**: Each node maintains own index
5. **Schema drift**: No version negotiation between nodes

## Health Check
```bash
# Local
python p9_search.py "test query" --db mac_memory.db

# Cross-node (when Tailscale up)
nats request agni.memory.search '{"query":"R_V"}'
```

## Blockers
| Issue | Impact | ETA |
|-------|--------|-----|
| Tailscale down | AGNI unreachable | Unknown |
| RUSHABDEV setup | 2K files unindexed | Awaiting his action |

---
**Next Review:** 2026-02-24  
**Owner:** INTEGRATOR subagent  
**Escalation:** If Tailscale not restored by 2026-02-20
