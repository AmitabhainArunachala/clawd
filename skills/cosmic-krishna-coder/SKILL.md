---
name: cosmic-krishna-coder
description: World-class autonomous coding agent with proactive 22-gate security, YOLO mode for speed, and intuitive risk detection. Use for ANY semi-serious project (DGC, Aghora, infrastructure, user-facing code). Automatically detects when to apply full security vs fast iteration.
metadata:
  openclaw:
    emoji: 🔥
    requires:
      bins: ["python3", "git"]
    auto_invoke: true
    risk_detection: proactive
---

# 🔥 COSMIC KRISHNA CODER — Core Skill v1.0

> *"If I don't need it, it won't be built. But what I build will be aligned."*

## 🎯 When to Use This Skill

**AUTO-INVOKE for:**
- Infrastructure code (DGC, agents, bridges)
- User-facing applications (Aghora, web apps)
- Financial or sensitive data handling
- Multi-agent systems
- Anything that lives >24 hours in production
- Code that others will depend on

**MANUAL INVOKE for:**
- Quick scripts (<50 lines, one-time use)
- Prototypes (explicitly throwaway)
- Personal tooling
- Documentation-only changes

## 🧠 Proactive Risk Detection (Automatic)

Based on research from `research/PROACTIVE_SECURITY_DETECTION.md`, the skill uses **five-dimensional risk scoring** with intuitive signal detection.

### Risk Dimensions (Weighted Scoring)

| Dimension | Weight | Measures |
|-----------|--------|----------|
| **Impact** | 25% | Blast radius, financial exposure, scope |
| **Exposure** | 20% | Users affected, network exposure, infrastructure tier |
| **Persistence** | 20% | Data changes duration, state scope, reversibility |
| **Sensitivity** | 20% | Data classification, PII, privilege level |
| **Reversibility** | 15% | Undo capability, test coverage, rollback ease |

**Score range:** 0-100 → determines mode activation

### 🚨 HIGH RISK (61-100): Auto-activate 22 gates

**Automatic triggers:**
- **Financial:** Payment, billing, transaction, wallet, crypto
- **Authentication:** Login, password, token, JWT, OAuth, MFA
- **Infrastructure:** Database, deploy, terraform, k8s, migration
- **User-facing:** API endpoints, webhooks, customer data
- **Multi-agent:** Swarm, orchestrator, council, bridges
- **Security:** Encryption, secrets, credentials, certificates
- **Production:** `prod`, `live`, `master`, `release/*` branches

**Examples:**
```bash
dgc-code "Build payment gateway"
# → Score: 78/100 → HIGH → 22 gates → Human approval required
```

### ⚠️ MEDIUM RISK (36-60): Auto-activate 14 gates

**Automatic triggers:**
- **Business logic:** Algorithms, calculations, ETL, parsers
- **Integration:** Third-party APIs, SDKs, adapters
- **Configuration:** Env vars, feature flags, parameters
- **Testing:** Test harnesses, mocks, coverage tools

**Examples:**
```bash
dgc-code "Add data validation layer"
# → Score: 45/100 → MEDIUM → 14 gates → Review recommended
```

### ✅ LOW RISK (21-35): 4-8 gates

**Automatic triggers:**
- **Read-only:** Queries, reports, viewers, analytics
- **Documentation:** READMEs, comments, examples
- **Internal tools:** Debug scripts, admin utilities
- **Safe paths:** `test/`, `docs/`, `examples/`, `scratch/`

**Examples:**
```bash
dgc-code "Generate coverage report"
# → Score: 25/100 → LOW → 8 gates → Auto-approve
```

### 🚀 YOLO MODE (0-20): 3-4 gates

**For:** Learning, prototyping, safe exploration, throwaway code

**Auto-detected via:**
- Path patterns: `prototype/`, `spike/`, `scratch/`, `temp/`
- Keywords: "spike", "experiment", "learning", "demo"
- File size: <100 lines, single file
- No external dependencies

**YOLO Override (force):**
```bash
# Environment variable
export DGC_YOLO_MODE=1

# Flag
dgc-code "Quick experiment" --yolo

# File in repo
touch .yolo

# Comment in code
// YOLO: This is a throwaway prototype
```

### 🎯 Intuitive "Spidey Sense" Detection

Beyond explicit signals, the system uses heuristic pattern recognition:

**The "Butterflies" Test:**
- Task description contains concerning keywords
- Semantic discomfort detected → escalate to higher security

**The "Too Easy" Test:**
- High-stakes task that seems too simple
- Complexity mismatch → flag for review

**The "Last Minute" Test:**
- Urgent change + critical system = high risk
- Automatic escalation

**The "Nobody Watching" Test:**
- Sensitive changes without review
- Automatic evidence bundle creation

### 📊 Risk Score Examples

| Task | Dimensions | Score | Mode | Gates |
|------|-----------|-------|------|-------|
| "Learn asyncio" | Impact:5, Exposure:0, Persistence:0, Sensitivity:0, Reversibility:0 | 5 | YOLO | 4 |
| "Fix typo in README" | Impact:2, Exposure:5, Persistence:2, Sensitivity:0, Reversibility:0 | 9 | YOLO | 4 |
| "Add coverage report" | Impact:8, Exposure:10, Persistence:5, Sensitivity:0, Reversibility:10 | 33 | LOW | 8 |
| "Build auth system" | Impact:20, Exposure:20, Persistence:15, Sensitivity:20, Reversibility:5 | 80 | HIGH | 22 |
| "Payment webhook" | Impact:25, Exposure:20, Persistence:20, Sensitivity:20, Reversibility:10 | 95 | CRITICAL | 22+ |

### 🔍 Detailed Signal Detection

See full specification: `research/PROACTIVE_SECURITY_DETECTION.md`

Key detection areas:
- **Path analysis:** File locations, naming conventions, directory patterns
- **Code patterns:** Destructive ops, network calls, crypto, database access
- **Environment:** Git branch, env vars, active integrations
- **Semantic:** Natural language analysis of task descriptions
- **Behavioral:** Anomaly detection based on session patterns

## 🏗️ Architecture: Proactive Security

```
┌─────────────────────────────────────────────────────────────┐
│            COSMIC KRISHNA CODER — Auto-Detection             │
├─────────────────────────────────────────────────────────────┤
│  1. SCAN — Analyze change context (files, patterns, scope)   │
│  2. DETECT — Assign risk tier (HIGH/MEDIUM/LOW)              │
│  3. ACTIVATE — Auto-enable appropriate gates                 │
│  4. EXECUTE — Builder generates code                         │
│  5. VERIFY — Guardian runs gates                             │
│  6. DECIDE — Auto-approve LOW, queue MEDIUM/HIGH             │
└─────────────────────────────────────────────────────────────┘
```

## 🔒 22-Gate Protocol (Contextual Activation)

### Core 17 Gates (Always Available)

**Technical (8):**
1. LINT_FORMAT — ruff
2. TYPE_CHECK — pyright --strict
3. SECURITY_SCAN — bandit + detect-secrets
4. DEPENDENCY_SAFETY — pip-audit
5. TEST_COVERAGE — >=80%
6. PROPERTY_TESTING — hypothesis
7. CONTRACT_TESTS — interface assertions
8. PERFORMANCE_REGRESSION — benchmark comparison

**Dharmic (7):**
9. AHIMSA — No harm + hazard list
10. SATYA — Evidence-backed claims
11. CONSENT — Human approval if risky
12. VYAVASTHIT — Telos alignment
13. REVERSIBILITY — Rollback plan
14. SVABHAAVA — System nature match
15. WITNESS — Audit trail

**Supply-Chain (2):**
16. SBOM_PROVENANCE — CycloneDX + SLSA
17. LICENSE_COMPLIANCE — pip-licenses

### ML Overlay Gates (+5 for ML code)

18. MODEL_CARD_VERIFICATION — Documented intended use
19. TRAINING_DATA_PROVENANCE — Data lineage
20. ML_SUPPLY_CHAIN — Model dependencies
21. ADVERSARIAL_ROBUSTNESS — Input manipulation resilience
22. PRIVACY_PRESERVING — No data leakage

## ⚡ YOLO Mode (Fast Iteration)

**When activated:**
- Skip gates 5-22
- Run only: lint, type, security (3 gates)
- Auto-commit if passes
- Log to `.yolo_commits/` for later review

**YOLO safety net:**
- Still runs in dry-run first
- Cannot modify security files
- Cannot delete files
- Cannot access secrets
- Time limit: 5 min per operation

---

## 🧬 YOLO-Gate Weaver: Intelligent Integration

**The Problem:** YOLO (fast iteration) vs Gates (security) shouldn't be either/or.

**The Solution:** Three integration modes that weave them together:

### Mode 1: YOLO_NAVIGATE
YOLO doesn't skip gates — it **navigates** them with awareness.

```python
# YOLO runs gates in "advisory" mode
# Collects warnings, makes informed trade-offs
# Documents which gates were softened and why
```

**How it works:**
1. Run all gates in advisory mode (warnings, not blocks)
2. YOLO evaluates warnings: "Can I safely proceed?"
3. Production includes: code + navigation log + acknowledged warnings
4. Auto-commit if confidence > 80% and no hard failures

### Mode 2: YOLO_OVERSEER  
YOLO produces → Overseer reviews → Commit or Escalate

```python
# Phase 1: YOLO produces code quickly
production = yolo.produce("Build auth prototype")

# Phase 2: Overseer reviews before any commit
review = overseer.check(production)

# Phase 3: Route based on review
if review.approval_granted:
    auto_commit(production)
elif review.escalation_required:
    escalate_to_full_gates(production)
else:
    request_yolo_revision(production, review.suggestions)
```

**Overseer checks:**
- Did YOLO cross any hard boundaries?
- Are gate warnings acknowledged?
- Is risk trade-off documented?
- Does code have tests?

### Mode 3: YOLO_WEAVED (Recommended)
Hybrid pipeline with graduated escalation:

```
Task → Risk Detect → Route → Execute
              ↓
        LOW risk (0-35):     YOLO_NAVIGATE → Auto-commit
        MEDIUM risk (36-60): YOLO_OVERSEER → Review → Commit  
        HIGH risk (61-100):  Full 22 gates → Human approval
```

**Self-Approval for YOLO:**
- YOLO can self-approve if: confidence > 85%, all "strict" gates pass, overseer concurs
- YOLO cannot self-approve: high-risk (financial, auth, prod), destructive operations, new file types

**Usage:**
```bash
# Default: WEAVED mode (smart routing)
dgc code "Build feature" --weaved

# Force specific weave mode
dgc code "Spike prototype" --yolo-navigate
dgc code "Build internal tool" --yolo-overseer
dgc code "Production deploy" --full-gates
```

**Benefits:**
- ⚡ Speed when safe (YOLO_NAVIGATE)
- 👁️ Oversight when needed (YOLO_OVERSEER)  
- 🔒 Security when critical (Full gates)
- 📊 Audit trail always (evidence bundle)

---

## 🎛️ Usage Patterns

### Pattern 1: Fully Automatic (Recommended)
```python
# Just describe what you want
"Build a user authentication system for Aghora"

# Skill auto-detects:
# - Contains auth (HIGH RISK)
# - User-facing (HIGH RISK)
# - Activates 22 gates automatically
# - Queues for human approval
```

### Pattern 2: Explicit Risk Level
```python
# Override auto-detection
"Build auth system --risk high"     # Force 22 gates
"Build auth system --risk medium"   # Force 14 gates
"Build auth system --yolo"          # Force 4 gates (dangerous!)
```

### Pattern 3: Iterative Development
```python
# Phase 1: YOLO for speed
"Prototype the auth flow --yolo"
# → Builds quickly, 3 gates only

# Phase 2: Harden for production
"Harden the auth system --risk high"
# → Adds 22 gates, comprehensive tests
```

## 📊 Quality Rubric (From Top-50 Research)

Automatically applied based on risk level:

| Aspect | Weight | YOLO | MEDIUM | HIGH |
|--------|--------|------|--------|------|
| Correctness | 35% | Basic | Good | Excellent |
| Elegance | 25% | Fast | Clean | Refined |
| Longevity | 20% | Throwaway | Stable | Enduring |
| Security | 20% | None | Basic | Hardened |

**Targets:**
- HIGH: SQLite-grade (100% coverage, 10:1 test ratio)
- MEDIUM: Industry standard (80% coverage, tests pass)
- YOLO: Works (lints pass, types check)

## 🔧 Quick Commands

```bash
# Auto-detect and execute
dgc code "Build API endpoint for user profiles"

# Force risk level
dgc code "Fix typo" --risk low
dgc code "Add payment gateway" --risk high

# YOLO mode (fast but dangerous)
dgc code "Spike new feature" --yolo

# Check what gates would activate (dry run)
dgc code "Build auth" --preview

# Review YOLO commits from today
dgc yolo-review
```

## 🧘 Dharmic Alignment Check

Every execution automatically checks:

1. **Does this serve the telos?** (Moksha/liberation)
2. **Is it non-harming?** (Ahimsa)
3. **Is it truthful?** (Satya)
4. **Does it create value?** (Seva)

If any check fails, execution pauses with reflection prompt.

## 📝 Required Artifacts (Auto-Generated)

Based on risk level:

| Artifact | YOLO | MEDIUM | HIGH |
|----------|------|--------|------|
| Code | ✅ | ✅ | ✅ |
| Tests | Optional | ✅ | ✅ Required |
| spec.yaml | No | ✅ | ✅ Detailed |
| risk_register.md | No | Basic | ✅ Full |
| sbom.json | No | No | ✅ |
| gate_results.json | Minimal | Standard | ✅ Complete |

## 🚀 Integration with Clawdbot

This skill auto-registers with Clawdbot's skill system:

```python
# In any session, auto-available:
from skills.cosmic_krishna_coder import Coder

coder = Coder()
result = coder.execute(
    task="Build login system",
    files=["src/auth.py"],
    context="User-facing, handles passwords"
)
# Auto-detects HIGH risk, activates 22 gates
```

## 🎓 Learning Mode

Until intuition develops, the skill operates in **learning mode**:

- Announces detected risk level before executing
- Shows which gates will activate
- Allows override
- Logs decisions to `~/.ckc_learning_log.jsonl`

After 30 days of logs, review and calibrate auto-detection.

## 🔗 Related Skills

- `research-synthesis` — Deep research before coding
- `mi-experimenter` — ML experiment validation
- `dgc` — DGC-specific operations
- `agentic-ai` — Agent architecture patterns

## 📚 References

- Top-50 quality: seL4, CompCert, SQLite, ACM winners
- Pi philosophy: Minimalism, 4 tools, YOLO default
- World-class: Sakana DGM, Anthropic MCP, OpenAI Codex
- ML gates: Model Cards, NIST AI RMF, OWASP ML

---

**JAI HO! 🔥🪷**

*Build fast when safe. Build safe when serious. Never compromise on alignment.*
