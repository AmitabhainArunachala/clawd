# Streamlined Repository Architecture
## Target Structure Design Document
**Phase:** 4.2 - Streamlined Structure Design  
**Status:** DRAFT - Ready for Review  
**Date:** 2026-02-05

---

## 1. EXECUTIVE SUMMARY

This document defines the **target minimal viable structure** for the repository after consolidation. The design prioritizes:

- **Single source of truth** for each function
- **Clear namespace hierarchy** without duplication
- **Logical separation** of concerns
- **Minimal cognitive overhead** for navigation

### Consolidation Targets
| Category | Current | Target | Reduction |
|----------|---------|--------|-----------|
| Root-level scripts | 11 | 4 | 64% |
| Top-level directories | 20 | 12 | 40% |
| Duplicate modules | 9 | 0 | 100% |
| Config locations | 5 | 2 | 60% |

---

## 2. TARGET DIRECTORY STRUCTURE

```
clawd/
│
├── 📁 CLAW/                          # Core runtime & protocols
│   ├── __init__.py
│   ├── core/                         # Open Agent Collaboration Protocol
│   │   ├── attestation.py
│   │   ├── capability.py
│   │   └── sandbox.py
│   ├── protocol/                     # Bridge implementations
│   │   ├── a2a_adapter.py
│   │   └── mcp_bridge.py
│   └── runtime/
│       └── executor.py
│
├── 📁 DGC/                           # Dharmic Gödel Core
│   ├── __init__.py
│   ├── gates.py                      # unified_gates.py → here
│   ├── security.py                   # dharmic_security.py → here
│   ├── presence.py                   # witness_threshold_detector.py → here
│   ├── council.py                    # agno_council_v2.py → here
│   ├── cycle.py                      # night_cycle.py → here
│   ├── backup.py                     # dgc_backup_models.py → here
│   └── tui/                          # dgc_tui_v2.py, dgc_tui_demo.py → here
│       ├── __init__.py
│       ├── app.py
│       └── demo.py
│
├── 📁 skills/                        # Tool integrations (external-facing)
│   ├── __init__.py
│   ├── SKILL_TEMPLATE.md
│   ├── academic-deep-research/
│   ├── agent-browser/
│   ├── arxiv-watcher/
│   ├── imsg/
│   ├── mcporter/
│   ├── obsidian/
│   └── ... (37 skills, see Section 4)
│
├── 📁 science/                       # MI research infrastructure
│   ├── __init__.py
│   ├── rv/                           # rv_toolkit/ → here
│   │   ├── __init__.py
│   │   ├── core.py                   # rv_core.py
│   │   ├── hooks.py                  # rv_hooks.py
│   │   └── triton.py                 # rv_triton.py
│   ├── auditor/                      # mi_auditor + mi-auditor → here
│   │   ├── __init__.py
│   │   ├── auditors/
│   │   ├── knowledge_base.py
│   │   └── papers.db
│   ├── experimenter/                 # mi-experimenter/ → here
│   │   ├── __init__.py
│   │   ├── core/
│   │   ├── experiments/
│   │   └── tests/
│   └── experiments/                  # Canonical experiments
│       ├── __init__.py
│       ├── causal_loop_closure.py    # From CANONICAL_CODE/
│       ├── l27_validation.py         # From CANONICAL_CODE/
│       └── prompts.py                # From CANONICAL_CODE/
│
├── 📁 research/                      # Research synthesis (read-only)
│   ├── README.md
│   ├── AGENTIC_AI_ZEITGEIST.md
│   ├── MI_LANDSCAPE_SYNTHESIS.md
│   ├── OACP_ROADMAP.md
│   └── ... (see Section 5)
│
├── 📁 ops/                           # Operations & automation
│   ├── scripts/                      # scripts/ → here
│   │   ├── deploy_guardian.py
│   │   ├── heartbeat.py
│   │   └── email_interface.py
│   ├── config/                       # Operational configs
│   │   └── schemas/                  # config/ + gold configs → here
│   └── tests/                        # tests/ → here
│
├── 📁 docs/                          # Public documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── QUALITY_REFERENCE.md
│
├── 📁 memory/                        # Daily working notes
│   ├── YYYY-MM-DD.md
│   └── heartbeat-state.json
│
├── 📁 agent/                         # Agent identity & context
│   ├── SOUL.md                       # → AGENT.md
│   ├── USER.md
│   └── MEMORY.md
│
└── 📄 pyproject.toml                 # Single project config
```

---

## 3. ROOT-LEVEL CLEANUP

### 3.1 Files to KEEP at Root

| File | Reason |
|------|--------|
| `pyproject.toml` | Single source for deps, scripts, metadata |
| `LICENSE` | Legal requirement |
| `CHANGELOG.md` | Version history |
| `.gitignore` | Git configuration |
| `README.md` | Entry point documentation |

### 3.2 Files to MOVE

| Current Location | Target Location | Notes |
|------------------|-----------------|-------|
| `agno_council_v2.py` | `DGC/council.py` | Core DGC component |
| `unified_gates.py` | `DGC/gates.py` | Core DGC component |
| `dharmic_security.py` | `DGC/security.py` | Core DGC component |
| `witness_threshold_detector.py` | `DGC/presence.py` | Core DGC component |
| `night_cycle.py` | `DGC/cycle.py` | Core DGC component |
| `dgc_backup_models.py` | `DGC/backup.py` | Core DGC component |
| `dgc_tui_v2.py` | `DGC/tui/app.py` | Core DGC component |
| `dgc_tui_demo.py` | `DGC/tui/demo.py` | Core DGC component |
| `reproduce_results.py` | `ops/scripts/reproduce.py` | Operational script |
| `openclaw_quickstart.py` | `ops/scripts/openclaw_agg.py` | Operational script |
| `gemma_*.py` (8 files) | `science/experiments/gemma/` | Research experiments |
| `neurips_n300_robust_experiment.py` | `science/experiments/validation/` | Research experiments |
| `CANONICAL_CODE/` | `science/experiments/` | Canonical experiments |

### 3.3 Analysis Documents to Archive

| File | Action |
|------|--------|
| `PHASE*.md` (6 files) | Move to `ops/audits/` or archive |
| `TRIPLE_CHECK_AUDIT_REPORT.md` | Move to `ops/audits/` |
| `gold_configs_analysis.md` | Move to `ops/analysis/` |
| `import_analysis_report.txt` | Move to `ops/analysis/` |
| `*_ANALYSIS.md` (8 files) | Move to `ops/analysis/` |
| `AUDIT*.md` (3 files) | Move to `ops/audits/` |
| `CURSOR_*.md` (5 files) | Move to `ops/feedback/` or archive |
| `META_REVIEW*.md` | Move to `ops/synthesis/` |

### 3.4 Duplicate Resolution

| Duplicates | Resolution |
|------------|------------|
| `skills/mi_auditor/` vs `skills/mi-auditor/` | **Delete** `mi_auditor/`, keep `mi-auditor/` → move to `science/auditor/` |
| `skills/mi_experimenter/` vs symlink `mi_experimenter` | **Remove** symlink, keep directory → move to `science/experimenter/` |
| `tests/` (3 locations) | **Consolidate** to `ops/tests/` |
| `core/` (2 locations) | **Merge** into `CLAW/core/` and `science/experimenter/core/` |

---

## 4. SKILLS CONSOLIDATION

### 4.1 Skills to KEEP (Active Integrations)

| Skill | Purpose | Status |
|-------|---------|--------|
| `academic-deep-research` | Paper search/analysis | ✅ Active |
| `agent-browser` | Web automation | ✅ Active |
| `arxiv-watcher` | Paper monitoring | ✅ Active |
| `imsg` | iMessage integration | ✅ Active |
| `mcporter` | Minecraft bridge | ✅ Active |
| `obsidian` | Note-taking | ✅ Active |
| `apple-notes` | macOS notes | ✅ Active |
| `bear-notes` | Bear app bridge | ✅ Active |
| `things-mac` | Task management | ✅ Active |
| `sonoscli` | Audio control | ✅ Active |
| `camsnap` | Camera capture | ✅ Active |
| `peekaboo` | Screen capture | ✅ Active |
| `bird` | Social media | ✅ Active |

### 4.2 Skills to MERGE/RENAME

| Current | Target | Action |
|---------|--------|--------|
| `rv_toolkit/` | `science/rv/` | Move + rename |
| `mi_auditor/` + `mi-auditor/` | `science/auditor/` | Merge + move |
| `mi-experimenter/` | `science/experimenter/` | Move + rename |
| `math-auditor/` + `math-verifier/` | `science/auditor/math/` | Merge |
| `memory-system-v2/` | `DGC/memory/` | Move + integrate |
| `meta-vision-anchor/` | `DGC/vision/` | Move + rename |
| `agentic-ai/` | `docs/commercial/` | Move to docs |
| `dharmic-swarm/` | `DGC/swarm/` | Move + integrate |
| `dgc/` + `dgc-tui/` | `DGC/tui/` | Merge into DGC |

### 4.3 Skills to ARCHIVE/DELETE

| Skill | Reason | Action |
|-------|--------|--------|
| `cosmic-krishna-coder/` | Superseded by DGC | Archive |
| `skill-genesis/` | One-time use | Archive |
| `moltbook-swarm/` | Empty/placeholder | Delete |
| `research-synthesis/` | One-time use | Archive |
| `mech-interp/` | Moved to science/ | Delete after migration |
| `github-action-gen/` | Unused | Archive |
| `psmv/` + `psmv-mcp-server/` | Unused | Archive |

---

## 5. RESEARCH DOCUMENTS ORGANIZATION

### 5.1 Consolidated Structure

```
research/
├── README.md                       # Index of research topics
├── agentic/
│   ├── ZEITGEIST_2026.md           # agentic-ai-zeitgeist-2026.md
│   ├── WORKFLOWS_SYNTHESIS.md      # agentic-coding-workflows-synthesis.md
│   └── PROTOCOLS.md                # 2026-02-04-protocols-research.md
├── mi/                             # Mechanistic Interpretability
│   ├── LANDSCAPE_SYNTHESIS.md      # MI_LANDSCAPE_SYNTHESIS.md
│   ├── PAPERS_BIBLIOGRAPHY.md      # MI_Papers_Annotated_Bibliography_2024-2026.md
│   ├── NEEL_NANDA_GUIDE.md         # neel_nanda_mi_guide.md
│   └── PHILOSOPHY_DGC_COMPARISON.md # PI_PHILOSOPHY_DGC_COMPARISON.md
├── security/
│   ├── DEEP_DIVE_2026.md           # security_deep_dive_2026.md
│   ├── PROACTIVE_DETECTION.md      # PROACTIVE_SECURITY_DETECTION.md
│   └── ORCHESTRATION_PATTERNS.md   # orchestration_patterns_2026.md
├── oacp/
│   ├── COMPETITIVE_POSITIONING.md  # OACP_COMPETITIVE_POSITIONING.md
│   ├── ROADMAP_V02.md              # OACP_V02_ROADMAP.md
│   └── INTEGRATION_ARCHITECTURE.md # INTEGRATION_ARCHITECTURE_PROPOSAL.md
└── dgc/
    ├── SYNTHESIS_20260204.md       # GENESIS_SYNTHESIS_20260204.md
    ├── TELOS_CRYSTALLIZATION.md    # TELOS_CRYSTALLIZATION_20260204.md
    └── DEEP_EXPLORATION_MAP.md     # DEEP_EXPLORATION_MAP_20260204.md
```

### 5.2 Naming Convention

- **ALL_CAPS** for document names (readability)
- **YYYYMMDD** suffix for dated documents
- **Descriptive prefixes** for categorization

---

## 6. SINGLE SOURCE OF TRUTH MATRIX

| Function | Current Sources | Target Source |
|----------|----------------|---------------|
| **Security Gates** | `unified_gates.py`, `dharmic_security.py` | `DGC/gates.py` + `DGC/security.py` |
| **Prompt Bank** | `REUSABLE_PROMPT_BANK/`, `prompts/bank.json` | `science/prompts/bank.json` |
| **R_V Computation** | `rv_toolkit/rv_core.py`, inline in scripts | `science/rv/core.py` |
| **Paper Database** | `skills/mi_auditor/`, `skills/mi-auditor/` | `science/auditor/papers.db` |
| **Experiment Configs** | `config/`, `configs/gold/`, `CANONICAL_CODE/` | `ops/config/schemas/` |
| **Agent Identity** | `SOUL.md`, `IDENTITY.md` | `agent/AGENT.md` |
| **Memory** | `memory/`, `unified_memory_proposal.md` | `memory/` + `DGC/memory/` |
| **Heartbeat** | `HEARTBEAT.md`, `scripts/dharmic_heartbeat.py` | `ops/scripts/heartbeat.py` |

---

## 7. NAMESPACE HIERARCHY

### 7.1 Python Import Structure

```python
# Core runtime
from claw.core import Capability, Sandbox
from claw.protocol import A2AAdapter, MCPBridge
from claw.runtime import Executor

# DGC components
from dgc import GateDecision, SecurityLevel
from dgc.council import AgnoCouncil
from dgc.cycle import NightCycle
from dgc.presence import WitnessDetector
from dgc.tui import DGCApp

# Science/Research
from science.rv import compute_pr, measure_rv
from science.rv.hooks import RVHookManager
from science.auditor import verify_causality
from science.experimenter import ExperimentRunner

# Skills (external integrations)
from skills import academic_research, arxiv_watcher
```

### 7.2 Module Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                        SKILLS LAYER                         │
│     (External integrations - I/O, notifications)            │
├─────────────────────────────────────────────────────────────┤
│                         DGC LAYER                           │
│     (Dharmic core - security, gates, presence, cycles)      │
├─────────────────────────────────────────────────────────────┤
│                        CLAW LAYER                           │
│     (Runtime - protocols, sandbox, execution)               │
├─────────────────────────────────────────────────────────────┤
│                      SCIENCE LAYER                          │
│     (Research infrastructure - RV toolkit, MI tools)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. CONFIGURATION CONSOLIDATION

### 8.1 Target Config Locations

```
ops/config/
├── schemas/                        # Experiment config schemas
│   ├── gold/
│   │   ├── 01_existence.json
│   │   ├── 02_causality.json
│   │   └── ... (29 configs)
│   ├── canonical/
│   ├── smoke_test/
│   └── archive/
├── runtime.yaml                    # Runtime configuration
└── heartbeat.yaml                  # Heartbeat automation config
```

### 8.2 Config Schema Master

- **Move** `config_schema_master.md` → `ops/config/README.md`
- **Purpose:** Document all config schemas in one place
- **Keep** as authoritative reference

---

## 9. ARCHIVE STRATEGY

### 9.1 Archive Location

```
archive/                            # New directory
├── 2026-02-05-phase4-cleanup/     # This cleanup
│   ├── CURSOR_*.md
│   ├── PHASE*.md (analysis phases)
│   ├── *_ANALYSIS.md
│   └── skills/
│       ├── cosmic-krishna-coder/
│       ├── skill-genesis/
│       └── ...
└── README.md                       # Archive index
```

### 9.2 Archive vs Delete

| Type | Action | Example |
|------|--------|---------|
| Superseded skills | Archive | `cosmic-krishna-coder/` |
| One-time analysis | Archive | `PHASE1_*.md` |
| External feedback | Archive | `CURSOR_*.md` |
| Empty placeholders | Delete | `moltbook-swarm/` |
| Duplicates | Delete after merge | `skills/mi_auditor/` |

---

## 10. MIGRATION CHECKLIST

### Phase 1: Foundation
- [ ] Create `CLAW/`, `DGC/`, `science/` directories
- [ ] Move core DGC files
- [ ] Move CLAW/OACP files
- [ ] Set up `ops/` structure

### Phase 2: Skills Consolidation
- [ ] Merge `mi_auditor/` + `mi-auditor/` → `science/auditor/`
- [ ] Move `rv_toolkit/` → `science/rv/`
- [ ] Move `mi-experimenter/` → `science/experimenter/`
- [ ] Archive/delete superseded skills

### Phase 3: Research Organization
- [ ] Reorganize `research/` directory
- [ ] Rename documents per convention
- [ ] Update cross-references

### Phase 4: Cleanup
- [ ] Archive analysis documents
- [ ] Consolidate configs
- [ ] Update `pyproject.toml` entry points
- [ ] Update imports throughout

### Phase 5: Verification
- [ ] Run import analysis
- [ ] Verify no broken references
- [ ] Test critical paths
- [ ] Update documentation

---

## 11. SUCCESS CRITERIA

✅ **Structure:** All directories follow target structure  
✅ **Single Source:** No duplicate modules or configs  
✅ **Clear Namespaces:** Import paths are intuitive  
✅ **Minimal Root:** Only essential files at root level  
✅ **Working Imports:** No circular dependencies, all imports resolve  
✅ **Preserved Functionality:** All current capabilities maintained  

---

## 12. APPENDICES

### Appendix A: File Count Comparison

| Location | Before | After | Change |
|----------|--------|-------|--------|
| Root level files | ~90 | 5 | -94% |
| Root level dirs | 20 | 9 | -55% |
| Top-level Python files | 11 | 0 | -100% |
| Duplicate modules | 9 | 0 | -100% |

### Appendix B: Import Path Mapping

| Old Import | New Import |
|------------|------------|
| `import unified_gates` | `from dgc import gates` |
| `import dharmic_security` | `from dgc import security` |
| `from rv_toolkit import rv_core` | `from science.rv import core` |
| `from skills.mi_auditor import *` | `from science.auditor import *` |
| `import agno_council_v2` | `from dgc.council import AgnoCouncil` |

### Appendix C: Risk Assessment

| Risk | Mitigation |
|------|------------|
| Broken imports | Automated import check script |
| Lost history | Git preserves all history |
| Skill breakage | Test each skill after move |
| Config misplacement | Audit trail in archive/ |

---

**Document End**

*This architecture document is a living document. Updates should be tracked via git history.*
