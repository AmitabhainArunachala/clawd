# ✅ MIGRATION CHECKLIST
## Quick Reference for Live Migration

Print this and check off as you go.

---

## PRE-MIGRATION (Do First!)

- [ ] **BACKUP CREATED**  
  `cp -r skills/agentic-ai /backup/agentic-ai-$(date +%Y%m%d)`

- [ ] **Git status clean**  
  `git status` shows no uncommitted changes

- [ ] **Current state documented**  
  `find . -type f | wc -l` = ___ files

---

## PHASE 1: FOUNDATION ⏱️ 10 min

| # | Task | Check | Command to Verify |
|---|------|-------|-------------------|
| 1 | Copy requirements.txt | [ ] | `test -f requirements.txt && echo ✓` |
| 2 | Copy LICENSE.md | [ ] | `test -f LICENSE.md && echo ✓` |
| 3 | Create .gitignore | [ ] | `test -f .gitignore && echo ✓` |

---

## PHASE 2: CORE DOCS ⏱️ 25 min

| # | Task | Check | Verify Content |
|---|------|-------|----------------|
| 4 | **MERGE skill.md** | [ ] | Has all sections from 3 sources |
|   | - Base: ./SKILL.md | [ ] | Research sections present |
|   | - Add: CLAWHUB examples | [ ] | Example code blocks present |
|   | - Add: FINAL pricing | [ ] | Pricing table present |
| 5 | **MERGE README.md** | [ ] | Marketing + technical |
|   | - Base: CLAWHUB/README | [ ] | Landing page quality |
|   | - Add: Install details | [ ] | Quickstart section |

**Merge Conflict Check:**  
- [ ] No `<<<<<<<` markers in skill.md  
- [ ] No `=======` markers in skill.md  
- [ ] No `>>>>>>>` markers in skill.md  

---

## PHASE 3: EXAMPLES ⏱️ 10 min

| # | Task | Check | Verify |
|---|------|-------|--------|
| 6 | Create examples/ dir | [ ] | `test -d examples && echo ✓` |
| 7 | Copy 01_hello_council.py | [ ] | From CLAWHUB_PACKAGE |
| 8 | Copy 02_spawn_specialist.py | [ ] | From CLAWHUB_PACKAGE |
| 9 | Copy 03_self_improvement.py | [ ] | From CLAWHUB_PACKAGE |
| 10 | Copy hello_agent.py | [ ] | From CLAWHUB_PACKAGE |
| 11 | **Test compilation** | [ ] | `python3 -m py_compile examples/*.py` |

---

## PHASE 4: EXTENDED DOCS ⏱️ 15 min

| # | Task | Check | Verify |
|---|------|-------|--------|
| 12 | Create docs/ dir | [ ] | `mkdir -p docs/marketing/reddit` |
| 13 | Move architecture.md | [ ] | From COMMERCIAL_PRODUCT_ARCHITECTURE |
| 14 | Move research.md | [ ] | From RESEARCH-2026-FRAMEWORKS |
| 15 | Create pricing.md | [ ] | Consolidated from PRICING.md |
| 16 | Move launch materials | [ ] | `mv LAUNCH_MATERIALS/* docs/marketing/` |

---

## PHASE 5: TEMPLATES & WEB ⏱️ 10 min

| # | Task | Check | Verify |
|---|------|-------|--------|
| 17 | Create templates/ dir | [ ] | `mkdir templates` |
| 18 | Copy quickstart.py | [ ] | From commercial-package |
| 19 | Copy custom_agent.py | [ ] | From commercial-package |
| 20 | Create web/ dir | [ ] | `mkdir web` |
| 21 | Move index.html | [ ] | `mv LANDING_PAGE/index.html web/` |

---

## PHASE 6: CLEANUP ⏱️ 10 min

**REMOVE these directories:**

- [ ] `commercial-package/`  
  Verify: `test ! -d commercial-package && echo ✓`

- [ ] `CLAWHUB_PACKAGE/`  
  Verify: `test ! -d CLAWHUB_PACKAGE && echo ✓`

- [ ] `COMMERCIAL_PACKAGE_FINAL/`  
  Verify: `test ! -d COMMERCIAL_PACKAGE_FINAL && echo ✓`

- [ ] `LAUNCH_MATERIALS/`  
  Verify: `test ! -d LAUNCH_MATERIALS && echo ✓`

- [ ] `LANDING_PAGE/` (if empty)  
  Verify: `test ! -d LANDING_PAGE && echo ✓`

**ARCHIVE these files:**

- [ ] Move root SKILL.md to `archive/` or keep with `_old` prefix
- [ ] Keep MARKET_RESEARCH_REPORT.md (reference)
- [ ] Keep PUBLISH_SUMMARY.md (reference)

---

## VALIDATION ⏱️ 15 min

### File Count Check

| Metric | Before | After | Pass? |
|--------|--------|-------|-------|
| Total files | 27+ | ~20 | [ ] |
| README files | 4 | 1 | [ ] |
| SKILL files | 3 | 1 | [ ] |
| Package dirs | 3 | 0 | [ ] |

### Required Files Present

- [ ] skill.md exists
- [ ] README.md exists  
- [ ] LICENSE.md exists
- [ ] requirements.txt exists

### Directories Present

- [ ] examples/ exists with 4 .py files
- [ ] docs/ exists with 3+ .md files
- [ ] templates/ exists with 2+ files
- [ ] web/ exists with index.html

### Directories Removed

- [ ] commercial-package/ removed
- [ ] CLAWHUB_PACKAGE/ removed
- [ ] COMMERCIAL_PACKAGE_FINAL/ removed
- [ ] LAUNCH_MATERIALS/ removed

### Content Validation

- [ ] skill.md has "PURPOSE" section
- [ ] skill.md has "Installation" section
- [ ] skill.md has "Quick Start" section
- [ ] skill.md has "Architecture" section
- [ ] README.md has "Quick Start" section
- [ ] README.md has "Features" section
- [ ] README.md has "Installation" section

### Technical Validation

- [ ] All Python examples compile: `python3 -m py_compile examples/*.py`
- [ ] No merge conflicts: `! grep -r "<<<<<<<" . --include="*.md"`
- [ ] No broken internal links: `grep -r "CLAWHUB_PACKAGE" . --include="*.md" | wc -l` = 0

---

## GIT COMMIT

- [ ] `git add .`
- [ ] `git status` reviewed
- [ ] Commit message written:

```
Consolidate packages: migrate 4 overlapping packages to single streamlined structure

- Merge 3 SKILL.md versions into single skill.md
- Consolidate 4 README.md into single README.md  
- Merge examples from multiple sources
- Create docs/ directory for extended content
- Create templates/ directory for starters
- Create web/ directory for landing page
- Remove commercial-package/, CLAWHUB_PACKAGE/, COMMERCIAL_PACKAGE_FINAL/

Before: 27+ files across 4 packages
After: ~20 files in single structure
Reduction: 26%
```

- [ ] `git commit` executed
- [ ] Commit hash: `____________________`

---

## POST-MIGRATION

- [ ] Test ClawHub upload with new structure
- [ ] Update any external documentation links
- [ ] Notify team of new structure
- [ ] Schedule backup cleanup (30 days)

---

## ROLLBACK (If Needed)

```bash
# Emergency rollback
cp -r /backup/agentic-ai-20260205/* .
git reset --hard HEAD~1
echo "Rollback complete"
```

**Rollback triggered:** [ ] Yes [ ] No  
**Reason:** _____________________________

---

## COMPLETION SIGN-OFF

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Migration Lead | | | |
| Technical Review | | | |
| Final Approval | | | |

**Migration Status:** [ ] COMPLETE [ ] ROLLED BACK [ ] PARTIAL

**Notes:**
_________________________________________________________________
_________________________________________________________________

---

**JSCA!** 🔥🪷  
*Checklist Version 1.0 - 2026-02-05*
