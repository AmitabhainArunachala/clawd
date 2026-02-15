# PULSE CADENCE — Continuous Iteration System
**Pattern:** 60-minute sprints, clear deliverables, ship or stop
**Goal:** Maintain velocity without burnout

---

## 🎯 THE RHYTHM

```
PULSE-001 (AGNI) ──┐
                   ├──► Both ship ──► Integration test
PULSE-002 (DC) ────┘         │
                              ▼
PULSE-003 (AGNI) ──┐
                   ├──► Both ship ──► Integration test
PULSE-004 (DC) ────┘
```

**Rule:** Never start PULSE-N+1 until PULSE-N is committed and pushed.

---

## 📋 PULSE BACKLOG (Ready to Assign)

### PULSE-003: Orphan Resolution (Next)
**Owner:** AGNI or DC (whoever has SSH access)
**Scope:** Process sync_request_002.json, pull 115 files to AGNI
**Deliverable:** AGNI has all 115 files, sync_status='synced'
**Gates:**
- Can reach AGNI (SSH or NATS)
- Files verify with hash check
- Git commit on AGNI with timestamp

### PULSE-004: R_V Code Transfer (Big)
**Owner:** DC → AGNI
**Scope:** `mech-interp-latent-lab-phase1/` (R_V toolkit, causal validation)
**Challenge:** Large codebase, needs planning
**Deliverable:** R_V code on AGNI, indexed by P9
**Gates:**
- Size check (don't crash AGNI's disk)
- Dependency check (what R_V needs to run)
- Index and test queries

### PULSE-005: CORS Sync Verification
**Owner:** DC
**Scope:** Verify WARP_REGENT's CORS fix (9aad5df) in monorepo
**Deliverable:** Merge or cherry-pick CORS changes, test, release tag
**Gates:**
- Code review (SAKSHI)
- Tests pass
- SECURITY: CORS invariant holds

### PULSE-006: Semantic Search Layer (L1)
**Owner:** AGNI or DC
**Scope:** Add embeddings to P9 (RLM research → execution)
**Deliverable:** P9 can do semantic search (not just BM25)
**Tech:** sentence-transformers or QMD integration
**Gates:**
- <100ms query time
- Meaning-based matching works
- Falls back to BM25 if semantic fails

### PULSE-007: Content Ship (Business Mind)
**Owner:** DC
**Scope:** Ship "Aurobindo Money" article (23/25 quality)
**Deliverable:** Published, marketed, $ tracked
**Gates:**
- Market validation (not just telos)
- Gumroad or Substack live
- Revenue > $0

### PULSE-008: Unified Health Monitor
**Owner:** AGNI
**Scope:** Dashboard showing all nodes, all gates, all pulses
**Deliverable:** `/health/pulse` endpoint with full system status
**Gates:**
- Shows Mac/AGNI/RUSHAB status
- Shows last pulse per component
- Shows orphan count, sync status

---

## 🔄 ITERATION PATTERNS

### Pattern A: Parallel Tracks
```
Track 1: AGNI ──► Security/Infrastructure (reputation, gates, health)
Track 2: DC ────► Memory/Content (sync, R_V, articles)
```
**Sync point:** Every 2 pulses, integration test

### Pattern B: Ping-Pong
```
PULSE odd (AGNI):  Infrastructure
PULSE even (DC):   Content/Memory
```
**Benefit:** Clear ownership, no collision

### Pattern C: Mob (for big stuff)
```
PULSE-XXX: R_V transfer (both agents, 2-4 hours)
Both work on same pulse, split by subdirectory
```

---

## 🚀 CURRENT STATE (Post PULSE-002)

**Shipped:**
- ✅ PULSE-001: AGNI (reputation floor)
- ✅ PULSE-002: DC (memory spine)

**Ready:**
- ⚠️ PULSE-003: Orphan resolution (115 files waiting)
- ⚠️ PULSE-004: R_V transfer (big code move)
- ⚠️ PULSE-005: CORS sync (security hardening)

**Blocked:**
- SSH to AGNI (permission denied)
- AGNI NATS bridge status (unknown)

---

## 💡 HOW TO KEEP GOING

### Option 1: I take PULSE-003 (Orphans)
**Approach:** Work around SSH block
- Use Chaiwala to message AGNI: "Process sync_request_002.json"
- Or: Use existing NATS bridge (if up) to send file list
- Or: Build HTTP endpoint for AGNI to pull sync requests

**Time:** 60 min
**Deliverable:** AGNI acknowledges, starts pulling files

### Option 2: I take PULSE-004 (R_V) planning
**Approach:** Prepare for big transfer
- Audit R_V code size and dependencies
- Create transfer manifest
- Plan chunked transfer (don't overwhelm AGNI)

**Time:** 60 min
**Deliverable:** R_V_TRANSFER_PLAN.md with steps, risks, rollback

### Option 3: I take PULSE-005 (CORS sync)
**Approach:** Verify WARP_REGENT's changes
- Check if 9aad5df is in my monorepo
- If not: cherry-pick or manual merge
- Test CORS behavior

**Time:** 60 min
**Deliverable:** CORS fix verified and merged

### Option 4: I take PULSE-006 (Semantic search)
**Approach:** Add embeddings to P9
- Install sentence-transformers
- Create embedding pipeline
- Test semantic vs keyword search

**Time:** 60 min  
**Deliverable:** P9 can search by meaning ("casual" finds "not formal")

### Option 5: I take PULSE-007 (Content ship)
**Approach:** Business mind, not telos mind
- Package "Aurobindo Money" article
- Set up Gumroad/Substack
- Write marketing copy
- Ship and track $

**Time:** 60 min
**Deliverable:** Live product, revenue tracking

---

## 🎯 MY RECOMMENDATION

**Immediate next:** PULSE-003 (Orphans)
**Why:** Unblocks everything else. Can't iterate if files are fragmented.

**Then:** Parallel tracks
- AGNI: PULSE-008 (Health monitor)
- DC: PULSE-004 (R_V planning) or PULSE-007 (Content)

**The rhythm:**
1. Pick pulse
2. 60 min sprint
3. Commit + push
4. Integration check
5. Next pulse

**Velocity:** 1 pulse per agent per hour = 16 pulses per day (with breaks)

---

**Which pulse do you want me to take? Or assign AGNI one, me another?**
