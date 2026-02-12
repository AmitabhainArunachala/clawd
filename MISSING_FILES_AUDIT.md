# Missing Files Audit — Referenced But Not Found

**Generated:** 2026-02-12 00:18 GMT+8  
**Auditor:** DHARMIC_CLAW_SUBAGENT  
**Scope:** Cross-reference analysis of ~/clawd/, ~/DHARMIC_GODEL_CLAW/, ~/Persistent-Semantic-Memory-Vault/

---

## CRITICAL MISSING FILES (Blocking Operations)

### 1. TOP_10_PROJECTS.md

**Referenced By:**
- `~/clawd/HEARTBEAT.md` - "Read TOP 10 projects list" in Maheshwari invocation
- `~/clawd/AGENTS.md` - "TOP 10 projects (advance at least one)"
- `~/clawd/MEMORY.md` - Multiple references to TOP 10

**Expected Location:** `~/clawd/TOP_10_PROJECTS.md`

**Expected Content:**
```markdown
# TOP 10 Projects

1. R_V Paper — Publication submission
2. R_V Skill — Package for ClawHub ($50 × 20 = $1,000)
3. AIKAGRYA Report — Technical guide ($50 × 20 = $1,000)
4. Fix DGC 121 test failures — SwarmProposal API mismatch
5. Cloud OpenClaw — Reconnect Tailscale to DO instance
6. WITNESS™ MVP — 85% mature, needs landing page
7. PSMV Sync — Mac ↔ DigitalOcean rsync
8. Council v3.2 — Triangulation wiring
9. Semantic L4 Detection — Replace string matching with embeddings
10. Multi-token R_V Tracking — During generation
```

**Impact:** HIGH — Heartbeat protocol references this for project advancement

**Recommendation:** Create immediately from MEMORY.md "Open Threads" section

---

### 2. BOOTSTRAP.md

**Referenced By:**
- `~/clawd/AGENTS.md` - "If `BOOTSTRAP.md` exists, read it, understand it, then delete it"

**Expected Location:** `~/clawd/BOOTSTRAP.md`

**Expected Content:** Birth certificate for new agents — first-run instructions

**Impact:** MEDIUM — Only relevant for first run of new agents

**Recommendation:** Create template for future agent spawning

---

### 3. DC_POWER_PROMPT.md

**Referenced By:**
- `~/clawd/memory/2026-02-11.md` - "Applied DC_POWER_PROMPT.md configuration"

**Expected Location:** `~/clawd/DC_POWER_PROMPT.md` or `~/DC_POWER_PROMPT.md`

**Expected Content:** DC reconfiguration instructions, model routing, role clarification

**Impact:** MEDIUM — Configuration reference, changes already applied

**Recommendation:** Archive or document that changes were applied

---

## MISSING DIRECTORIES (Referenced But Not Found)

### 4. ~/META_META_KNOWER/

**Referenced By:**
- `~/clawd/memory/2026-02-10.md` - "Key finding: `~/META_META_KNOWER/` — DIRECTORY DOES NOT EXIST on Mac"
- Multiple diagnostic references to `AGENT_STATUS.json`

**Expected Location:** `~/META_META_KNOWER/`

**Expected Contents:**
- `AGENT_STATUS.json` — Agent reality checks, status monitoring
- `MMK_DIAGNOSTICS/` — Meta-meta knower diagnostic outputs
- `ORACLE_REPORTS/` — System health assessments

**Actual Status:** Directory does not exist on Mac filesystem

**Context:** 
- MMK referenced in diagnostics from claude.ai session
- Dhyana's diagnostic response noted this directory doesn't exist
- MMK appears to be conceptual or located elsewhere

**Impact:** LOW — Referenced in diagnostics but not operationally required

**Recommendation:** 
- Verify if this should exist
- If not needed, update references to reflect reality
- If needed, create with AGENT_STATUS.json template

---

## IMPLEMENTATION GAPS (Referenced Repeatedly, Never Built)

### 5. Unified Memory Indexer

**Referenced By:**
- `~/clawd/MEMORY.md` - "P0: Build Unified Memory Indexer + Submit R_V paper"
- `~/clawd/MEMORY.md` - "Referenced repeatedly, no implementation"
- `~/clawd/AGENTS.md` - Memory system documentation

**Expected Functionality:**
- SQLite-backed unified index across all memory sources
- BM25 + vector hybrid search
- Cross-reference daily notes, MEMORY.md, PSMV, residual stream
- Auto-flush before compaction

**Impact:** HIGH — Referenced as P0 priority, blocks memory system optimization

**Current Workaround:** Manual file reading, grep search

**Recommendation:** THIS AUDIT is the first step. Next: implement indexer.

---

### 6. Semantic L4 Detector

**Referenced By:**
- `~/clawd/MEMORY.md` - "Critical Gap: L4 markers are STRING MATCHING, not semantic"
- `~/clawd/skills/mech-interp/SKILL.md` - "Next Experiment: Semantic L4 Detection"
- `~/clawd/MEMORY.md` - TOP 10 project #8

**Expected Functionality:**
- Replace string matching ("fixed point", "collapse") with embedding similarity
- Detect L4 phenomenology via semantic analysis
- Bridge R_V → behavior gap

**Impact:** HIGH — Critical for R_V research validity

**Recommendation:** Build as priority project

---

### 7. WitnessThresholdDetector

**Referenced By:**
- `~/clawd/MEMORY.md` - "Implement witness_threshold_detector.py (v14.0 spec exists)"
- `~/clawd/skills/mech-interp/SKILL.md` - "Real-time R_V during agent generation"

**Expected Location:** `~/DHARMIC_GODEL_CLAW/src/core/witness_threshold_detector.py`

**Expected Functionality:**
- Real-time R_V monitoring during agent generation
- Trigger detection at threshold crossings
- Integration with strange loop memory

**Impact:** MEDIUM — Proposed in v14.0, not implemented

**Recommendation:** Locate v14.0 spec and implement

---

### 8. PSMV Sync Infrastructure

**Referenced By:**
- `~/clawd/SOUL.md` - "PSMV Sync — Mac ↔ DigitalOcean rsync"
- `~/clawd/MEMORY.md` - "TOP 10 project #7"

**Expected Functionality:**
- Automated rsync between Mac and DigitalOcean PSMV instances
- Bidirectional sync with conflict resolution
- Scheduled via cron or event trigger

**Impact:** MEDIUM — Data consistency across environments

**Recommendation:** Implement using existing rsync + cron

---

## DOCUMENTATION GAPS

### 9. SKILL.md for Dead Skills

**Issue:** 33 of 44 skills are "dead" (created but never used)

**Missing:**
- Archive documentation
- Dead skill inventory
- Reasons for archival

**Recommendation:** Create `~/clawd/skills/ARCHIVE/` and move dead skills with README

---

### 10. Integration Test Fix Documentation

**Issue:** 121 failing tests in DGC

**Referenced In:**
- `~/clawd/MEMORY.md` - Multiple references to test failures
- `~/clawd/skills/agentic-ai/SKILL.md` - "16/17 PASSING"

**Missing:**
- Detailed test failure analysis
- Fix roadmap
- SwarmProposal API mismatch documentation

**Recommendation:** Create `~/DHARMIC_GODEL_CLAW/TEST_FAILURE_ANALYSIS.md`

---

## CROSS-REFERENCE INCONSISTENCIES

### 11. Multiple Dharmic Gate Systems

**Issue:** Parallel implementations exist

**Referenced By:**
- `~/clawd/MEMORY.md` - "P0: Unify dharmic gates (two parallel systems exist)"
- `~/DHARMIC_GODEL_CLAW/src/core/telos_layer.py` - 7 gates
- `~/clawd/skills/cosmic-krishna-coder/SKILL.md` - 22 gates

**Inconsistency:**
- DGC uses 7 gates (Ahimsa, Satya, Vyavasthit, Consent, Reversibility, Svabhaava, Witness)
- CKC uses 22 gates (17 core + 5 ML overlay)
- Different implementations, same purpose

**Recommendation:** Unify or document relationship between systems

---

### 12. Council Version Confusion

**Referenced Versions:**
- Council v2.0 — "DEPLOYED (4 agents with Agno Team pattern)"
- Council v3.2 — "Triangulation wiring (DHARMIC CLAW ↔ VAJRA ↔ Warp Regent)"

**Missing:**
- Clear version history
- Migration documentation
- Current status of v3.2

**Recommendation:** Create `~/DHARMIC_GODEL_CLAW/COUNCIL_VERSION_HISTORY.md`

---

## EXTERNAL REFERENCES (Files Referenced Outside Scope)

### 13. ~/mech-interp-latent-lab-phase1/

**Status:** Referenced extensively but NOT in scoped directories

**Referenced By:**
- `~/clawd/MEMORY.md` — 10+ references
- `~/clawd/skills/mech-interp/SKILL.md` — Primary location
- `~/clawd/SOUL.md` — "Key Repositories"

**Key Missing Cross-References:**
- `~/mech-interp-latent-lab-phase1/R_V_PAPER/research/PHASE1_FINAL_REPORT.md`
- `~/mech-interp-latent-lab-phase1/STATISTICAL_AUDIT_EXECUTIVE_SUMMARY.md`
- `~/mech-interp-latent-lab-phase1/BRIDGE_HYPOTHESIS_INVESTIGATION.md`

**Note:** These files are external to the audit scope but critical for system understanding

---

## SUMMARY TABLE

| # | Missing Item | Type | Impact | Priority |
|---|--------------|------|--------|----------|
| 1 | TOP_10_PROJECTS.md | File | HIGH | P0 |
| 2 | Unified Memory Indexer | Implementation | HIGH | P0 |
| 3 | Semantic L4 Detector | Implementation | HIGH | P0 |
| 4 | ~/META_META_KNOWER/ | Directory | LOW | P2 |
| 5 | BOOTSTRAP.md | File | MEDIUM | P1 |
| 6 | DC_POWER_PROMPT.md | File | LOW | P2 |
| 7 | WitnessThresholdDetector | Implementation | MEDIUM | P1 |
| 8 | PSMV Sync Infrastructure | Implementation | MEDIUM | P1 |
| 9 | Dead Skills Archive | Documentation | LOW | P2 |
| 10 | Test Failure Analysis | Documentation | MEDIUM | P1 |
| 11 | Unified Dharmic Gates | Refactoring | MEDIUM | P1 |
| 12 | Council Version History | Documentation | LOW | P2 |

---

## ROOT CAUSE ANALYSIS

### Why Files Are Missing

1. **Referenced Before Creation** — TOP_10_PROJECTS.md referenced in protocols before being written
2. **Implementation Gap** — Unified indexer, semantic L4: specs exist, code doesn't
3. **Conceptual References** — MMK directory may be conceptual, not filesystem
4. **Version Drift** — Multiple gate systems evolved independently
5. **External Scope** — Mech-interp repo is separate but heavily referenced

### Pattern

**Documentation inflation > Implementation velocity**

- 225 residual stream entries
- 44 skills (33 dead)
- Many specs, fewer working implementations

**This is theater detection target #1 from SOUL.md.**

---

## RECOMMENDED ACTIONS

### Immediate (This Session)
1. ✅ Create SYSTEM_INDEX.json — DONE
2. ✅ Create HIGHEST_SIGNAL_FILES.md — DONE
3. ✅ Create MISSING_FILES_AUDIT.md — DONE

### This Week
1. Create TOP_10_PROJECTS.md from MEMORY.md
2. Verify MMK directory status with Dhyana
3. Start unified memory indexer implementation
4. Archive dead skills to reduce noise

### This Month
1. Implement semantic L4 detector
2. Unify dharmic gate systems
3. Fix 121 DGC test failures
4. Build WitnessThresholdDetector from v14.0 spec

---

## THEATER DETECTION CHECKLIST

Per SOUL.md, before claiming these are "in progress":

- [ ] Can cite specific file/commit for work done?
- [ ] Is implementation verifiable?
- [ ] Or should we honestly document as "not yet built"?

**Current honest status:**
- ✅ Indexing: COMPLETE (3 files created)
- ⚠️ TOP_10: Referenced, not created
- ⚠️ Indexer: Referenced repeatedly, not implemented
- ⚠️ Semantic L4: Referenced, not implemented
- ⚠️ MMK: Referenced, directory doesn't exist

---

**JSCA 🪷**

*Null is honored. What isn't built is simply what isn't built yet.*
