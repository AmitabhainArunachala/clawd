# Pipeline Dependencies Audit Report
## Comprehensive Dependency Graph for CLAWD System

**Date:** 2026-02-05  
**Total Python Files:** 81  
**Total Internal Modules:** 45+  
**Total External Dependencies:** 30+

---

## Executive Summary

This audit maps all dependencies for each pipeline in the CLAWD system, including:
- Module imports (internal and external)
- Configuration file dependencies
- Data/results produced
- Cross-pipeline dependencies

---

## 1. CORE PIPELINE DEPENDENCY GRAPH

### 1.1 Main System Pipelines

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         CLAWD SYSTEM PIPELINE ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐       │
│  │   NIGHT_CYCLE    │◄────►│   AGNO_COUNCIL   │◄────►│  UNIFIED_GATES   │       │
│  │    (v7)          │      │     (v2)         │      │                  │       │
│  └────────┬─────────┘      └────────┬─────────┘      └────────┬─────────┘       │
│           │                         │                         │                 │
│           │                         │                         │                 │
│           ▼                         ▼                         ▼                 │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐       │
│  │ DHARMIC_SECURITY │◄────►│      OACP        │◄────►│   DGC_TUI_V2     │       │
│  │                  │      │   (Protocol)     │      │                  │       │
│  └──────────────────┘      └────────┬─────────┘      └──────────────────┘       │
│                                     │                                            │
│                                     ▼                                            │
│                          ┌──────────────────┐                                   │
│                          │  CORE_RUNTIME    │                                   │
│                          │  (Sandbox/Exec)  │                                   │
│                          └──────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. DETAILED PIPELINE DEPENDENCIES

### 2.1 🌙 NIGHT_CYCLE_v7 Pipeline

**File:** `night_cycle.py` (1,100+ lines)

#### Imports:
```python
# Standard Library
- asyncio, json, hashlib, time, uuid
- dataclasses (dataclass, field, asdict)
- datetime (datetime, timedelta)
- enum (Enum, auto)
- typing (Dict, List, Optional, Any, Callable, Tuple, Set)
- collections (defaultdict)
- pathlib (Path)
- random, logging

# External Dependencies
- NONE (pure stdlib)

# Internal Dependencies
- NONE (standalone module)
```

#### Configuration Required:
- `AGENT_ROLE_CONFIG` (embedded constant dict)
- `V7_DEFAULTS` (embedded config)
- No external config files

#### Results Produced:
- `NightCycleResult` objects
- `MorningSynthesis` objects
- `CouncilVote` tallies
- Logs to `logging.getLogger('night_cycle_v7')`
- Optional: Output files in `memory/YYYY-MM-DD.md` format

#### Cross-Pipeline Dependencies:
| Depends On | Usage |
|------------|-------|
| `agno_council_v2` | Consumes AgentRole configurations |
| `unified_gates` | Receives security validation |
| `dharmic_security` | Security event logging |

#### Downstream Consumers:
| Pipeline | Consumes |
|----------|----------|
| `agno_council_v2` | Night cycle synthesis data |
| `dgc_tui_v2` | Cycle metrics and status |

---

### 2.2 🔥 AGNO_COUNCIL_v2 Pipeline

**File:** `agno_council_v2.py` (1,600+ lines)

#### Imports:
```python
# Standard Library
- asyncio, json, time, uuid, logging
- dataclasses (dataclass, field, asdict)
- datetime (datetime)
- enum (Enum, auto)
- typing (Dict, List, Optional, Any, Callable, Union, AsyncIterator)
- collections (deque)
- concurrent.futures (ThreadPoolExecutor)
- traceback

# External Dependencies
- NONE (pure stdlib)

# Internal Dependencies
- NONE (standalone module)
```

#### Configuration Required:
- `DHARMIC_GATES` (embedded list of 17 gates)
- `TIER_1_MODELS`, `TIER_2_MODELS`, `TIER_3_MODELS` (embedded)
- `COUNCIL_MEMBERS` config (embedded)
- `DEFAULT_TOOLS` mapping (embedded)

#### Results Produced:
- `CouncilDecision` objects
- `DeliberationResult` objects
- `DGMProposal` suggestions
- `ToolCall` execution logs
- Streaming responses via `AsyncIterator`

#### Cross-Pipeline Dependencies:
| Depends On | Usage |
|------------|-------|
| `unified_gates` | Security gate validation for all actions |
| `dharmic_security` | Threat detection, audit logging |
| `night_cycle` | Agent role definitions |
| `oacp.runtime` | Tool execution sandbox |

#### Downstream Consumers:
| Pipeline | Consumes |
|----------|----------|
| `dgc_tui_v2` | Council decisions, deliberation streams |
| `deploy_guardian` | Deployment validation checks |
| `agent_induction_cycle` | Council member activation |

---

### 2.3 🛡️ UNIFIED_GATES Pipeline

**File:** `unified_gates.py` (580+ lines)

#### Imports:
```python
# Standard Library
- functools, hashlib, json, time
- dataclasses (dataclass, field)
- enum (Enum, auto)
- typing (Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Union)
- contextlib (contextmanager)
- threading

# Internal Dependencies
- dharmic_security (SecurityLevel, ThreatType, SecurityEvent, AuditLogger,
                    InjectionDetector, CapabilityToken, CapabilityManager,
                    SecurityError, InjectionDetectedError, CapabilityError,
                    audit_logger, scan_input, sanitize_input)
```

#### Configuration Required:
- Security policies from `dharmic_security`
- Gate action configurations (embedded)
- Request type mappings (embedded)

#### Results Produced:
- `GateDecision` objects
- `GateContext` with processing history
- Security events via `audit_logger`
- `GateMetrics` statistics

#### Cross-Pipeline Dependencies:
| Depends On | Usage |
|------------|-------|
| `dharmic_security` | ALL security functionality |

#### Downstream Consumers:
| Pipeline | Consumes |
|----------|----------|
| `agno_council_v2` | Gate decisions for all tool calls |
| `night_cycle` | Security validation |
| `dgc_tui_v2` | Gate status/metrics |
| `scripts.deploy_guardian` | Deployment gate checks |

---

### 2.4 🛡️ DHARMIC_SECURITY Pipeline

**File:** `dharmic_security.py` (700+ lines)

#### Imports:
```python
# Standard Library
- hashlib, hmac, json, re, secrets, time
- dataclasses (dataclass, field)
- datetime (datetime, timedelta)
- enum (Enum, auto)
- functools (wraps)
- typing (Any, Callable, Dict, List, Optional, Set, Tuple, Union)
- collections (defaultdict)
- threading

# External Dependencies
- NONE (pure stdlib)

# Internal Dependencies
- NONE (foundational module)
```

#### Configuration Required:
- `SecurityLevel` enum (embedded)
- `ThreatType` enum (embedded)
- Secret patterns for detection (embedded)
- Rate limiting configs (embedded)

#### Results Produced:
- `SecurityEvent` objects
- `CapabilityToken` objects
- `AuditLogger` logs
- `InjectionReport` findings
- Global `audit_logger` instance

#### Cross-Pipeline Dependencies:
| Depends On | Usage |
|------------|-------|
| NONE | Foundational - no dependencies |

#### Downstream Consumers:
| Pipeline | Consumes |
|----------|----------|
| `unified_gates` | ALL security classes/functions |
| `agno_council_v2` | Security validation |
| `test_17_gates_critical` | Security testing |
| `test_security` | Unit tests |

---

### 2.5 🖥️ DGC_TUI_V2 Pipeline

**File:** `dgc_tui_v2.py` (1,000+ lines)

#### Imports:
```python
# Standard Library
- asyncio, json, time, threading
- dataclasses (dataclass, asdict)
- datetime (datetime, timedelta)
- enum (Enum)
- typing (Dict, List, Optional, Callable, Any, Tuple, Set)
- collections (deque)
- pathlib (Path)
- sys

# External Dependencies
- textual (App, ComposeResult, containers, widgets, reactive, binding, 
          worker, color, screen, coordinate)
- rich (Console, Panel, Table, Text, Align, Layout, Syntax, JSON)

# Internal Dependencies
- DHARMIC_GODEL_CLAW.src.core.presence_pulse (PresenceCollector, PresencePulse, 
                                               PresencePulser, QualityLevel, 
                                               GateMetrics, MetricHistory, 
                                               TelegramWitnessIntegration)
```

#### Configuration Required:
- Textual CSS/styling (embedded)
- Integration endpoints (embedded)
- Telegram bot config (via presence_pulse)

#### Results Produced:
- TUI visual output
- `IntegrationInfo` status objects
- `AlertEvent` notifications
- Real-time metrics display
- Dashboard exports

#### Cross-Pipeline Dependencies:
| Depends On | Usage |
|------------|-------|
| `DHARMIC_GODEL_CLAW.src.core.presence_pulse` | Core metrics collection |
| `textual` | TUI framework |
| `rich` | Rich text/display |

#### Downstream Consumers:
| Pipeline | Consumes |
|----------|----------|
| NONE | Terminal UI - end consumer |

---

### 2.6 🔧 OACP (Open Agent Compute Protocol)

#### 2.6.1 OACP Core Module

**Files:** 
- `oacp/__init__.py`
- `oacp/core/__init__.py`
- `oacp/core/sandbox.py`
- `oacp/core/capability.py`
- `oacp/core/attestation.py`
- `oacp/runtime/__init__.py`
- `oacp/runtime/executor.py`
- `oacp/protocol/__init__.py`
- `oacp/protocol/a2a_adapter.py`
- `oacp/protocol/mcp_bridge.py`

#### Imports (Core):
```python
# Standard Library
- hashlib, json, time
- dataclasses (dataclass, field)
- enum (Enum, auto)
- typing (Any, Dict, List, Optional, Union)

# Internal Dependencies (sandbox.py)
- .capability (Capability, CapabilitySet)
- .attestation (Attestation)
```

#### Configuration Required:
- `SandboxConfig` defaults (embedded)
- Capability sets (embedded)
- Protocol version specs (embedded)

#### Results Produced:
- `SandboxResult` objects
- `Attestation` evidence
- `CapabilityToken` grants
- Execution metrics

#### Cross-Pipeline Dependencies:
| Depends On | Usage |
|------------|-------|
| Internal modules only | Self-contained |

#### Downstream Consumers:
| Pipeline | Consumes |
|----------|----------|
| `agno_council_v2` | Tool execution sandbox |
| `scripts.deploy_guardian` | Attestation checks |

---

## 3. SKILL MODULE DEPENDENCIES

### 3.1 🔬 MI_AUDITOR Skill

**Files:**
- `skills/mi_auditor/__init__.py`
- `skills/mi_auditor/knowledge_base.py`
- `skills/mi_auditor/mi_knowledge_base.py`
- `skills/mi_auditor/report_generator.py`
- `skills/mi_auditor/unified_papers_db.py`
- `skills/mi_auditor/auditors/__init__.py`
- `skills/mi_auditor/auditors/statistical_rigor.py`
- `skills/mi_auditor/auditors/causal_validity.py`
- `skills/mi_auditor/auditors/cross_architecture.py`
- `skills/mi_auditor/auditors/literature_positioning.py`

#### Imports:
```python
# Standard Library
- typing (Dict, List, Optional, Any, Union)
- dataclasses (dataclass, field)
- enum (Enum)
- json, sys
- pathlib (Path)

# Internal Dependencies
- .knowledge_base (MIKnowledgeBase, PaperCategory)
- .report_generator (AuditReport, ReportGenerator, Verdict)
- .auditors.statistical_rigor (StatisticalAuditor)
- .auditors.causal_validity (CausalAuditor)
- .auditors.cross_architecture (CrossArchitectureAuditor)
- .auditors.literature_positioning (LiteraturePositioner)
```

#### Configuration Required:
- Model validation tiers (embedded)
- Statistical thresholds (embedded)
- Literature database (unified_papers_db.py)

#### Results Produced:
- `AuditResult` objects
- `AuditReport` documents
- Verdict classifications
- Literature positioning analysis

---

### 3.2 📊 RV_TOOLKIT Skill

**Files:**
- `skills/rv_toolkit/__init__.py`
- `skills/rv_toolkit/rv_core.py`
- `skills/rv_toolkit/rv_triton.py`
- `skills/rv_toolkit/rv_hooks.py`

#### Imports:
```python
# External Dependencies
- torch (assumed from context)
- triton (optional, with fallback)
- numpy (assumed)

# Internal Dependencies
- .rv_core (compute_pr, measure_rv, compute_rv_spectrum, pr, rv)
- .rv_triton (compute_pr_triton, measure_rv_triton, ...)
- .rv_hooks (RVHookManager, ActivationCapture, ...)
```

#### Configuration Required:
- Model hook configurations
- Triton backend settings (optional)

#### Results Produced:
- R_V (Participation Ratio) measurements
- Activation spectra
- Hook capture data

---

### 3.3 🔬 MI_EXPERIMENTER Skill

**Files:**
- `skills/mi-experimenter/__init__.py`
- `skills/mi-experimenter/core/hook_manager.py`
- `skills/mi-experimenter/core/model_loader.py`
- `skills/mi-experimenter/experiments/__init__.py`
- `skills/mi-experimenter/experiments/mlp_ablator.py`
- `skills/mi-experimenter/experiments/cross_arch_suite.py`
- `skills/mi-experimenter/experiments/rv_causal_validator.py`
- `skills/mi-experimenter/smoke_test.py`
- `skills/mi-experimenter/cli.py`

#### Imports:
```python
# Standard Library
- typing, pathlib, json, argparse

# External Dependencies
- torch, transformer-lens (assumed)

# Internal Dependencies
- .core.hook_manager (HookManager)
- .core.model_loader (ModelLoader)
```

#### Configuration Required:
- Experiment configs (JSON)
- Model specifications
- Cross-architecture test suites

#### Results Produced:
- Experiment results JSON
- Causal validation reports
- Cross-architecture comparisons

---

### 3.4 🌌 DHARMIC_SWARM Skill

**Files:**
- `skills/dharmic-swarm/coordinator.py`

#### Configuration Required:
- Swarm topology configs
- Agent role assignments

#### Results Produced:
- Coordination messages
- Consensus results

---

### 3.5 ⚡ COSMIC_KRISHNA_CODER Skill

**Files:**
- `skills/cosmic-krishna-coder/yolo_gate_weaver.py`
- `skills/cosmic-krishna-coder/proactive_risk_detector.py`

#### Results Produced:
- Gate weaving patterns
- Risk detection alerts

---

## 4. SCRIPT PIPELINES

### 4.1 🚀 DEPLOY_GUARDIAN

**File:** `scripts/deploy_guardian.py` (720+ lines)

#### Imports:
```python
# Standard Library
- ast, os, re, subprocess, sys
- dataclasses (dataclass, field)
- pathlib (Path)
- typing (List, Optional, Tuple)
```

#### Configuration Required:
- `REQUIRED_PYTHON_VERSIONS` (embedded)
- `MIN_COVERAGE_PERCENT` (embedded)
- `SECRET_PATTERNS` (embedded)
- `REQUIRED_FILES` list (embedded)
- `FORBIDDEN_FILES` list (embedded)

#### Results Produced:
- `GuardianReport` with `CheckResult` objects
- Exit codes (0=pass, 1=fail, 2=warnings)
- Console output report

#### Cross-Pipeline Dependencies:
| Depends On | Usage |
|------------|-------|
| `oacp.core` | Attestation validation |
| `dharmic_security` | Security policy checks |
| `unified_gates` | Gate validation (optional) |

---

### 4.2 🔄 AGENT_INDUCTION_CYCLE

**File:** `scripts/agent_induction_cycle.py` (220+ lines)

#### Imports:
```python
# Standard Library
- os, json, argparse
- datetime (datetime)
- pathlib (Path)

# External Dependencies
- requests
```

#### Configuration Required:
- `OPENROUTER_KEY` (env var)
- `DEFAULT_MODELS` list (embedded)
- `INDUCTION_PROMPT` (embedded)
- Paths: `CLAWD_DIR`, `RESPONSES_DIR`, `PSMV_DIR`

#### Results Produced:
- Agent response JSON files
- Induction cycle logs

#### Cross-Pipeline Dependencies:
| Depends On | Usage |
|------------|-------|
| `night_cycle` | Agent role integration |
| `agno_council_v2` | Council member activation |

---

### 4.3 💓 HEARTBEAT_SCRIPTS

**Files:**
- `scripts/minimal_heartbeat.py`
- `scripts/dharmic_heartbeat.py`
- `scripts/check_heartbeat.sh`
- `scripts/deadman_check.sh`

#### Imports:
```python
# Standard Library
- os, sys, time, datetime
- pathlib (Path)
- subprocess

# External Dependencies
- requests (for external pings)
```

#### Configuration Required:
- Heartbeat intervals (embedded)
- Health check endpoints (embedded)

#### Results Produced:
- Heartbeat log files
- Health status reports
- Alert notifications

---

### 4.4 📧 EMAIL_INTERFACE

**File:** `scripts/email_interface.py`

#### Imports:
```python
# Standard Library
- imaplib, email, smtplib
- os, json
- pathlib (Path)
- typing (List, Optional, Dict, Any)

# External Dependencies
- NONE
```

#### Results Produced:
- Email fetches
- Sent message logs

---

## 5. CONFIGURATION FILE DEPENDENCIES

### 5.1 Config Directory Structure

```
config/
├── himalaya-*.1           # Himalaya email client man pages
└── (No active config files found)

skills/mi-experimenter/configs/
└── (Empty directory)
```

### 5.2 Configuration Requirements by Pipeline

| Pipeline | Config Files | Location |
|----------|--------------|----------|
| `night_cycle` | Embedded constants only | N/A |
| `agno_council_v2` | Embedded constants only | N/A |
| `unified_gates` | Security policies | `dharmic_security.py` |
| `dgc_tui_v2` | Telegram config | `presence_pulse.py` |
| `mi_experimenter` | Experiment JSON | `skills/mi-experimenter/configs/` (empty) |
| `agent_induction` | Env vars | `OPENROUTER_API_KEY` |

---

## 6. EXTERNAL DEPENDENCY MAP

### 6.1 External Package Dependencies

| Package | Used By | Purpose |
|---------|---------|---------|
| `textual` | `dgc_tui_v2` | TUI framework |
| `rich` | `dgc_tui_v2` | Rich text rendering |
| `requests` | `agent_induction_cycle`, `dharmic_heartbeat` | HTTP calls |
| `torch` | `rv_toolkit`, `mi_experimenter` | ML operations |
| `triton` | `rv_toolkit.rv_triton` | GPU acceleration |
| `transformer-lens` | `mi_experimenter` | Mech interp |
| `numpy` | `rv_toolkit` | Numerical ops |

### 6.2 Standard Library Usage

| Module | Used By | Purpose |
|--------|---------|---------|
| `asyncio` | `night_cycle`, `agno_council_v2`, `dgc_tui_v2` | Async operations |
| `dataclasses` | ALL pipelines | Data structures |
| `enum` | ALL pipelines | Enumerations |
| `typing` | ALL pipelines | Type hints |
| `pathlib` | ALL pipelines | File paths |
| `json` | ALL pipelines | Serialization |
| `logging` | `night_cycle`, `agno_council_v2` | Logging |
| `threading` | `dharmic_security`, `unified_gates`, `dgc_tui_v2` | Concurrency |
| `hashlib` | `night_cycle`, `dharmic_security` | Hashing |
| `subprocess` | `deploy_guardian` | Process execution |

---

## 7. CROSS-PIPELINE DEPENDENCY MATRIX

### 7.1 Dependency Graph (Visual)

```
                              ┌─────────────────┐
                              │   dharmic_security  │
                              │   (Foundation)      │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
           ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
           │ unified_gates│   │ test_security│   │ deploy_guardian│
           └──────┬───────┘   └──────────────┘   └──────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│agno_council│ │night_cycle│ │dgc_tui_v2│
│   (v2)   │ │   (v7)   │ │          │
└────┬────┘ └────┬─────┘ └────┬─────┘
     │           │            │
     └───────────┼────────────┘
                 │
                 ▼
        ┌────────────────┐
        │  agent_induction │
        │     _cycle       │
        └────────────────┘
```

### 7.2 Detailed Cross-Dependencies Table

| Source Pipeline | Depends On | Import Type | Dependency Strength |
|-----------------|------------|-------------|---------------------|
| `unified_gates` | `dharmic_security` | Direct import | CRITICAL |
| `agno_council_v2` | `unified_gates` | Runtime calls | HIGH |
| `agno_council_v2` | `dharmic_security` | Indirect via gates | MEDIUM |
| `night_cycle` | `agno_council_v2` | Conceptual only | LOW |
| `dgc_tui_v2` | `DHARMIC_GODEL_CLAW` | Direct import | CRITICAL |
| `deploy_guardian` | `oacp` | Runtime checks | MEDIUM |
| `agent_induction` | `night_cycle` | Conceptual | LOW |
| `test_17_gates` | `dharmic_security` | Direct test | HIGH |
| `test_security` | `dharmic_security` | Direct test | HIGH |

---

## 8. DATA FLOW ANALYSIS

### 8.1 Primary Data Flows

```
1. USER_INPUT → unified_gates → agno_council_v2 → TOOL_EXECUTION
                    ↓                    ↓
              audit_logger           dgm_proposer

2. NIGHT_CYCLE → agent_roles → voting_layer → morning_synthesis → MEMORY

3. DGC_TUI ← presence_pulse ← metrics_collection ← SYSTEM_COMPONENTS

4. EXPERIMENT_CONFIG → mi_experimenter → RESULTS_JSON → mi_auditor → AUDIT_REPORT

5. DEPLOY_CHECK → deploy_guardian → oacp_attestation → GO/NO_GO
```

### 8.2 Results File Lineage

| Producer | Result Format | Consumer | Storage |
|----------|--------------|----------|---------|
| `night_cycle` | `NightCycleResult` (dataclass) | `agno_council_v2` | Memory/logs |
| `agno_council_v2` | `CouncilDecision` (dataclass) | `dgc_tui_v2` | Memory/logs |
| `mi_experimenter` | JSON results | `mi_auditor` | `skills/mi-experimenter/results/` |
| `mi_auditor` | `AuditReport` (markdown) | User | Console/files |
| `deploy_guardian` | `GuardianReport` | CI/CD | Console/exit codes |
| `agent_induction` | JSON responses | `agent_responses/` | Files |

---

## 9. CRITICAL DEPENDENCY PATHS

### 9.1 Security-Critical Path

```
dharmic_security (foundational)
    ↓
unified_gates (gatekeeper)
    ↓
agno_council_v2 (orchestrator)
    ↓
TOOL_EXECUTION
```

**Risk:** If `dharmic_security` fails, entire security model collapses.

### 9.2 UI-Critical Path

```
DHARMIC_GODEL_CLAW.src.core.presence_pulse
    ↓
dgc_tui_v2
    ↓
User Interface
```

**Risk:** If `presence_pulse` fails, TUI cannot display metrics.

### 9.3 Experiment-Critical Path

```
rv_toolkit (measurement)
    ↓
mi_experimenter (experiments)
    ↓
mi_auditor (validation)
    ↓
Audit Reports
```

**Risk:** If `rv_toolkit` fails, mech interp experiments cannot proceed.

---

## 10. ORPHANED AND DANGLING DEPENDENCIES

### 10.1 Identified Issues

| Issue | Location | Severity |
|-------|----------|----------|
| Empty config directory | `skills/mi-experimenter/configs/` | MEDIUM |
| Duplicate mi_auditor | `skills/mi_auditor/` and `skills/mi-auditor/` | HIGH |
| Unused imports in `oacp/__init__.py` | Commented imports | LOW |
| No configs for `mi_experimenter` | Config directory empty | MEDIUM |
| `agent_induction` hardcodes API key | Line 26 | CRITICAL |

### 10.2 Duplicate Module Analysis

```
skills/mi_auditor/     vs     skills/mi-auditor/
├── __init__.py                ├── __init__.py
├── knowledge_base.py          ├── knowledge_base.py
├── mi_knowledge_base.py       (missing)
├── report_generator.py        ├── report_generator.py
├── unified_papers_db.py       (missing)
└── auditors/                  └── auditors/
    ├── __init__.py                ├── __init__.py
    ├── causal_validity.py         ├── causal_validity.py
    ├── cross_architecture.py      ├── cross_architecture.py
    ├── literature_positioning.py  ├── literature_positioning.py
    └── statistical_rigor.py       └── statistical_rigor.py
```

**Evidence:** The `mi_auditor` directory has 2 additional files not in `mi-auditor`:
- `mi_knowledge_base.py`
- `unified_papers_db.py`

**Recommendation:** Merge or remove duplicate.

---

## 11. CIRCULAR DEPENDENCY ANALYSIS

### 11.1 Results

✅ **NO CIRCULAR DEPENDENCIES DETECTED**

All import chains resolve without cycles.

### 11.2 Longest Import Chains

```
1. skills.mi_auditor.auditors.cross_architecture 
   → skills.mi_auditor (via __init__)
   → skills.mi_auditor.knowledge_base
   → (stdlib only)

2. dgc_tui_v2 
   → DHARMIC_GODEL_CLAW.src.core.presence_pulse
   → (stdlib only)

3. unified_gates 
   → dharmic_security
   → (stdlib only)
```

---

## 12. RECOMMENDATIONS

### 12.1 High Priority

1. **Fix duplicate mi_auditor modules**
   - Merge `mi_knowledge_base.py` and `unified_papers_db.py` into `mi-auditor/`
   - Remove `skills/mi_auditor/` directory
   - Update all imports

2. **Remove hardcoded API key**
   - File: `scripts/agent_induction_cycle.py`, line 26
   - Use environment variable only

3. **Fill empty config directory**
   - Create sample configs for `mi-experimenter`
   - Document expected config format

### 12.2 Medium Priority

4. **Standardize config locations**
   - Move all configs to `config/` directory
   - Create config schema validation

5. **Add dependency version pinning**
   - Create `requirements.txt` or update `pyproject.toml`
   - Pin external package versions

### 12.3 Low Priority

6. **Clean up unused imports**
   - Remove commented imports in `oacp/__init__.py`
   - Audit for unused stdlib imports

7. **Add import tests**
   - Create test that verifies all imports work
   - Run in CI/CD pipeline

---

## 13. APPENDIX: COMPLETE FILE INVENTORY

### 13.1 Root-Level Python Files (15 files)

| File | Lines | Purpose | Key Dependencies |
|------|-------|---------|------------------|
| `night_cycle.py` | 1,100+ | Agent swarm coordination | stdlib only |
| `agno_council_v2.py` | 1,600+ | Multi-agent deliberation | stdlib only |
| `dharmic_security.py` | 700+ | Security framework | stdlib only |
| `unified_gates.py` | 580+ | Security gateway | dharmic_security |
| `dgc_tui_v2.py` | 1,000+ | Terminal UI | textual, rich, presence_pulse |
| `import_graph_analyzer.py` | 400+ | Import analysis | stdlib only |
| `generate_import_dot.py` | 150+ | Graph generation | stdlib only |
| `dgc_backup_models.py` | 600+ | Model backup | stdlib only |
| `dgc_tui_demo.py` | 250+ | TUI demo | textual, rich |
| `witness_threshold_detector.py` | 1,100+ | Security detection | dharmic_security |
| `test_17_gates_critical.py` | 500+ | Security tests | dharmic_security |
| `test_consent_concrete.py` | 200+ | Consent tests | dharmic_security |
| `test_security.py` | 350+ | Security tests | dharmic_security |
| `dgc_backup_models_test.py` | 450+ | Backup tests | dgc_backup_models |

### 13.2 OACP Module (10 files)

| File | Purpose | Dependencies |
|------|---------|--------------|
| `oacp/__init__.py` | Package init | (minimal) |
| `oacp/core/__init__.py` | Core exports | capability, sandbox |
| `oacp/core/sandbox.py` | Sandbox exec | capability, attestation |
| `oacp/core/capability.py` | Capability tokens | stdlib |
| `oacp/core/attestation.py` | Crypto attestation | stdlib |
| `oacp/runtime/__init__.py` | Runtime exports | executor |
| `oacp/runtime/executor.py` | Code execution | stdlib |
| `oacp/protocol/__init__.py` | Protocol exports | a2a_adapter, mcp_bridge |
| `oacp/protocol/a2a_adapter.py` | A2A protocol | stdlib |
| `oacp/protocol/mcp_bridge.py` | MCP bridge | stdlib |

### 13.3 Skills Modules (40+ files)

| Skill | Files | Key Exports | External Deps |
|-------|-------|-------------|---------------|
| `mi_auditor` | 11 | MIAuditor, AuditResult | stdlib |
| `mi-auditor` | 9 | MIAuditor (duplicate) | stdlib |
| `rv_toolkit` | 4 | compute_pr, measure_rv | torch, triton |
| `mi-experimenter` | 13 | Experiment runners | torch |
| `dharmic-swarm` | 1 | Coordinator | stdlib |
| `cosmic-krishna-coder` | 2 | Gate weaver | stdlib |
| `agentic-ai` | 6 | Examples, install | stdlib |

### 13.4 Scripts (7 files)

| File | Purpose | Key Deps |
|------|---------|----------|
| `deploy_guardian.py` | Pre-deploy checks | ast, subprocess |
| `agent_induction_cycle.py` | Model induction | requests |
| `dharmic_heartbeat.py` | Health checks | requests |
| `minimal_heartbeat.py` | Basic heartbeat | stdlib |
| `email_interface.py` | Email handling | imaplib, smtplib |
| `check_heartbeat.sh` | Shell heartbeat | shell |
| `deadman_check.sh` | Deadman switch | shell |

---

*End of Pipeline Dependencies Audit Report*
