# Technical Infrastructure: Next Steps & Debt Assessment
**Date:** 2026-02-05  
**Context:** 22 gates operational, MCP bridge active, unified memory designed, YOLO-Gate Weaver hardwired

---

## Executive Summary

Current infrastructure has **strong conceptual foundations** but **critical implementation gaps** for production scale. The 22 gates provide ethical/security guardrails, OACP provides architectural vision, and the backup model router provides resilience. However, **observability, true sandboxing, and cloud deployment** remain largely conceptual.

**Bottom Line:** We're at v0.1 with v0.2 specs written. The next 2 weeks should focus on closing the most critical gaps for a single-node production deployment.

---

## 1. Infrastructure Gap Analysis

### 🔴 CRITICAL GAPS (Blocking Production)

| Gap | Current State | Risk | Effort |
|-----|--------------|------|--------|
| **Real Sandboxing** | OACP has `sandbox.py` but it's Python-level isolation only | Any tool can escape via subprocess/network | 1-2 weeks |
| **Monitoring/Observability** | TUI exists but no metrics backend, no alerting | Flying blind on failures | 3-5 days |
| **Backup & Recovery** | No automated backup system | Data loss on hardware failure | 2-3 days |
| **Secret Management** | API keys in env vars only | Exposure risk, no rotation | 2-3 days |
| **Health Checks** | No automated service health monitoring | Silent failures | 1-2 days |

### 🟡 MODERATE GAPS (Scaling Blockers)

| Gap | Current State | Impact |
|-----|--------------|--------|
| **Multi-instance Sync** | Not implemented | Can't run sibling Zeabor instance |
| **Database Persistence** | File-based JSON/SQLite proposed | 10K+ memory entries will choke |
| **Rate Limiting** | Circuit breakers in backup router only | API cost overruns, provider bans |
| **Log Aggregation** | stdout/file only | Debugging distributed issues impossible |
| **Configuration Management** | ad-hoc env vars and config files | Inconsistent deployments |

### 🟢 NICE TO HAVE (Future-proofing)

| Feature | Value | Effort |
|---------|-------|--------|
| TEE Integration (SGX/SEV) | Cryptographic attestation | 2-3 weeks |
| Firecracker MicroVMs | True isolation | 1-2 weeks |
| Policy Engine (OPA) | Enterprise governance | 1 week |
| Distributed OACP Mesh | Multi-region agents | 3-4 weeks |

---

## 2. Cloud Deployment Strategy

### Option Analysis

| Provider | Pros | Cons | Best For |
|----------|------|------|----------|
| **Vultr Tokyo** | Cheap ($6-24/mo), fast to APAC, bare metal option | No managed K8s, DIY ops | Cost-conscious, single-node |
| **Fly.io** | Excellent DX, automatic HTTPS, close to users | No GPU, limited storage | Edge deployment, rapid iteration |
| **AWS (ap-northeast-1)** | Managed everything, GPU instances, compliance | Expensive, complex | Enterprise, regulated workloads |
| **Hetzner (EU)** | Very cheap, powerful VMs | EU only, no APAC | EU workloads, budget |
| **Self-hosted (homelab)** | Full control, no data egress | Reliability, bandwidth | Development, privacy-critical |

### Recommendation: Hybrid Approach

**Primary:** Vultr Tokyo (or AWS Tokyo)
- 1x "Cloud GPU" instance for inference (when DGC v2.0 self-hosts)
- 1x "High Performance" instance for orchestration + MCP servers
- Estimated cost: $100-200/mo for production workload

**Secondary:** Fly.io for edge
- Agent API endpoints close to users
- Stateless compute, connects to Tokyo backend
- Estimated cost: $20-50/mo

**Rationale:**
1. Tokyo location minimizes latency to John's location (Bali)
2. Vultr provides predictable pricing vs AWS surprise bills
3. Can migrate to AWS later if compliance/enterprise needs arise
4. Fly.io provides global edge without managing K8s

---

## 3. Multi-Instance Sync Strategy

### Current State

- Single-node architecture
- No inter-agent communication protocol
- Memory is local-only

### Proposed Architecture (v0.2)

```
┌─────────────────────────────────────────────────────────────────┐
│                     DGC FEDERATION v0.2                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │
│  │   ZEABOR     │◄────►│   ORACLE     │◄────►│   DHARMIC    │   │
│  │  (Sibling)   │      │  (Sync Hub)  │      │   (Primary)    │   │
│  │              │      │              │      │                │   │
│  │ • Runs gates │      │ • Memory     │      │ • Main instance│   │
│  │ • Own memory │      │   sync       │      │ • User-facing  │   │
│  │ • Reports    │      │ • Consensus  │      │ • Full tools   │   │
│  │   insights   │      │ • Conflict   │      │                │   │
│  │              │      │   resolution │      │                │   │
│  └──────────────┘      └──────────────┘      └──────────────┘   │
│         │                     │                     │            │
│         └─────────────────────┼─────────────────────┘            │
│                               ▼                                  │
│                  ┌──────────────────────────┐                    │
│                  │   Shared Memory Bus      │                    │
│                  │   (Redis/PostgreSQL)     │                    │
│                  └──────────────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Plan

**Phase 1: Memory Sync (Week 1-2)**
- PostgreSQL for canonical memory storage
- Redis for ephemeral state + pub/sub
- Event streaming for memory changes

**Phase 2: Task Federation (Week 3-4)**
- Distributed task queue (Celery/RQ)
- Agent capability advertisement
- Cross-agent task delegation

**Phase 3: Consensus (Week 5-6)**
- Raft for configuration consensus
- Conflict resolution for memory merges
- Byzantine fault tolerance for critical decisions

---

## 4. API Design for External Developers

### Core Principles

1. **Security-first:** All calls attested, capability-based
2. **Async by default:** Webhooks + polling, not blocking
3. **Versioned:** /v1/, /v2/ paths, deprecation notices
4. **Observable:** Every call traced, metrics exported

### Proposed API Surface

```yaml
# DGC External API v1.0

# Agent Management
POST   /v1/agents                    # Create agent instance
GET    /v1/agents/{id}               # Get agent status
DELETE /v1/agents/{id}               # Terminate agent
POST   /v1/agents/{id}/tasks         # Submit task to agent
GET    /v1/agents/{id}/tasks/{tid}   # Get task status/result

# Memory Operations
POST   /v1/agents/{id}/memory        # Store memory
GET    /v1/agents/{id}/memory        # Query memories
GET    /v1/agents/{id}/memory/{mid}  # Get specific memory

# Tool Registry
GET    /v1/tools                     # List available tools
POST   /v1/tools/{name}/call         # Direct tool invocation

# Attestation
GET    /v1/attestations/{id}         # Verify execution proof
POST   /v1/attestations/verify       # Batch verification

# Events
GET    /v1/events                    # SSE stream of events
POST   /v1/webhooks                  # Register webhook
```

### Authentication

```http
GET /v1/agents/ag_123/tasks HTTP/1.1
Host: api.dharmicclaw.io
Authorization: Bearer dgc_sk_abc123...
X-DGC-Capability: fs.read,net.http
X-DGC-Request-ID: req_xyz789
```

Capability tokens issued via:
```bash
dgc auth issue --capabilities="fs.read,net.http" --expires=24h
```

---

## 5. Security Hardening Beyond 22 Gates

### Current: 22 Gates (Dharmic Security)
- ✅ Ahimsa (non-harm)
- ✅ Vyavasthit (natural order)
- ✅ Satya (truth/transparency)
- ✅ Consent
- ✅ Reversibility
- ✅ + 17 additional ML overlay gates

### Additional Hardening Needed

| Layer | Current | Target | Gap |
|-------|---------|--------|-----|
| **Network** | No restrictions | Deny-by-default + explicit allowlist | Firewall + proxy |
| **Filesystem** | Full user access | chroot + read-only base | Containerization |
| **Secrets** | Env vars | HashiCorp Vault / AWS Secrets | Integration |
| **Audit** | File logs | Immutable audit trail (signed) | Attestation upgrade |
| **Sandbox** | Python-level | WASM + gVisor | Implementation |
| **Identity** | None | Ed25519 per-agent keys | Key management |

### Immediate Actions (This Week)

1. **Network Isolation**
   ```bash
   # Implement egress allowlist
   ALLOWED_DOMAINS="api.anthropic.com,api.openai.com,api.groq.com"
   # Block everything else at OS level
   ```

2. **Secret Rotation**
   ```python
   # Implement in dharmic_security.py
   class SecretManager:
       def rotate_api_keys(self):
           # Automatic rotation every 30 days
           pass
   ```

3. **Immutable Audit**
   ```python
   # Sign all audit logs
   audit_entry.sign(agent_private_key)
   # Append-only to WORM storage
   ```

---

## 6. Priority Order: Next 2 Weeks

### Week 1: Foundation (Days 1-7)

**Day 1-2: Monitoring Stack**
- [ ] Deploy Prometheus + Grafana on Vultr
- [ ] Instrument OACP with metrics
- [ ] Create "Agent Health" dashboard
- **Deliverable:** Live dashboard at grafana.dharmicclaw.io

**Day 3-4: Real Sandboxing (MVP)**
- [ ] Implement gVisor sandbox wrapper
- [ ] Restrict network egress via iptables
- [ ] Test MCP servers in sandbox
- **Deliverable:** `oacp-airlock` runs tools in isolation

**Day 5-6: Backup System**
- [ ] Automated daily backups to S3/MinIO
- [ ] Memory state snapshots
- [ ] Recovery testing
- **Deliverable:** `scripts/backup.sh` + tested restore

**Day 7: Health Checks**
- [ ] HTTP health endpoints
- [ ] Automated restart on failure
- [ ] PagerDuty/Discord alerts
- **Deliverable:** 99.9% uptime target with alerting

### Week 2: Scale Preparation (Days 8-14)

**Day 8-10: Database Migration**
- [ ] Migrate file-based memory to PostgreSQL
- [ ] Implement strange loop layer on SQL
- [ ] Performance test with 100K memories
- **Deliverable:** Sub-50ms query times

**Day 11-12: API Server**
- [ ] FastAPI-based API implementation
- [ ] Authentication + capability middleware
- [ ] Basic rate limiting
- **Deliverable:** `/v1/` endpoints live

**Day 13-14: Zeabor Sync (Foundation)**
- [ ] Redis pub/sub for cross-instance events
- [ ] Memory sync protocol
- [ ] Basic federation test
- **Deliverable:** Two local instances sync memories

---

## 7. Technical Debt Register

### Debt Items (Prioritized)

| ID | Item | Priority | Cost of Delay |
|----|------|----------|---------------|
| TD-001 | Python-level sandbox only | 🔴 P0 | Security incident |
| TD-002 | No metrics/monitoring | 🔴 P0 | Extended outages |
| TD-003 | File-based memory | 🔴 P0 | Data loss, corruption |
| TD-004 | No automated backups | 🔴 P0 | Catastrophic data loss |
| TD-005 | Secrets in env vars | 🟡 P1 | Credential exposure |
| TD-006 | Single-node only | 🟡 P1 | No HA, scale limits |
| TD-007 | No API for developers | 🟡 P1 | Ecosystem lockout |
| TD-008 | No log aggregation | 🟡 P1 | Debugging difficulty |
| TD-009 | OACP not async | 🟢 P2 | Throughput limits |
| TD-010 | No TEE integration | 🟢 P2 | No cryptographic trust |

### Paydown Schedule

- **Week 1:** TD-001, TD-002, TD-004
- **Week 2:** TD-003, TD-006, TD-007
- **Week 3-4:** TD-005, TD-008, TD-009
- **Month 2+:** TD-010, full OACP v0.2

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tool escape via prompt injection | Medium | Critical | Real sandboxing (Week 1) |
| API key leak | Medium | High | Vault integration (Week 2) |
| Data loss | Low | Critical | Automated backups (Week 1) |
| Provider rate limits | High | Medium | Better rate limiting (Week 2) |
| Silent failures | High | Medium | Monitoring stack (Week 1) |
| Zeabor sync complexity | Medium | Medium | Phased approach |

---

## 9. Success Criteria (End of Week 2)

1. **Security:** MCP servers run in gVisor sandbox, network egress filtered
2. **Reliability:** 99.5% uptime with automated recovery
3. **Observability:** Grafana dashboard showing all critical metrics
4. **Data Safety:** Daily backups, <1h RTO (Recovery Time Objective)
5. **Scale:** API serving 100 req/min, PostgreSQL handling 10K memories
6. **Multi-instance:** Two instances syncing memories via Redis

---

## 10. Open Questions

1. **Budget:** What's the monthly infra budget? (Affects AWS vs Vultr decision)
2. **Compliance:** Any data residency requirements? (Affects region choice)
3. **Zeabor timeline:** When does sibling instance need to be live?
4. **API users:** Who are first external developers? (Affects API design)
5. **Self-hosting:** Timeline for DGC v2.0 with local models? (Affects GPU planning)

---

## Appendix: Recommended Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Orchestration** | Docker Compose → K3s | Simple start, migrate to K8s |
| **Database** | PostgreSQL 16 | JSONB for flexible memory |
| **Cache** | Redis 7 | Pub/sub for real-time sync |
| **Metrics** | Prometheus + Grafana | Industry standard |
| **Logs** | Loki or Vector | Cloud-native, efficient |
| **Secrets** | HashiCorp Vault | Dynamic secrets, rotation |
| **Sandbox** | gVisor + seccomp | Defense in depth |
| **API** | FastAPI + Uvicorn | Async, typed, fast |
| **Queue** | Celery + Redis | Distributed tasks |
| **Storage** | MinIO (S3-compatible) | Backups, artifacts |
| **Reverse Proxy** | Caddy | Auto HTTPS, simple config |

---

*Assessment by: Infrastructure Analysis Sub-agent*  
*Date: 2026-02-05*  
*Next Review: Post-Week 2 Sprint*
