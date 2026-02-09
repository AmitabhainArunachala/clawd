---
title: "ANTI-SLOP QUALITY PROTOCOL — 3-Layer Toyota-Style"
version: "1.0"
created: "2026-02-10"
for: "AGNI prototyping"
requestor: "Dhyana (via DHARMIC_CLAW)"
---

# 🏭 ANTI-SLOP QUALITY PROTOCOL
## 3-Layer Final Check Before SHIP

**Core Principle:** Every deliverable must pass 3 hard gates before publication. No exceptions. No rushing. Quality over speed.

---

## LAYER 1: AUTOMATED VALIDATION (Machine Check)
**Gatekeeper:** Scripts, tests, linters
**Time:** 5-15 minutes
**Pass Criteria:** All green

### Code Deliverables
```
□ All tests pass (pytest/cargo test)
□ Linting clean (black/flake8/clippy)
□ Type checking (mypy)
□ No secrets/credentials in code (detect-secrets)
□ Documentation builds (mkdocs/sphinx)
□ Security scan (bandit/semgrep)
```

### Content Deliverables (Articles, Guides)
```
□ Grammar/spelling (LanguageTool/proselint)
□ Readability score (Hemingway/flesch-kincaid < grade 12)
□ Plagiarism check (unique content > 90%)
□ Link validation (no 404s)
□ Fact verification (citations check)
```

### Product Deliverables (Skills, Tools)
```
□ Installation test (clean environment)
□ Basic functionality test (smoke test)
□ Documentation accuracy (commands work)
□ Error handling (graceful failures)
```

**Output:** `layer1_validation_report.json`
**Fail Action:** Fix → Re-run Layer 1
**Pass Action:** Proceed to Layer 2

---

## LAYER 2: PEER REVIEW (Human/Agent Check)
**Gatekeeper:** Another agent or human reviewer
**Time:** 15-30 minutes
**Pass Criteria:** 2+ approvals

### Review Checklist
```
□ Does it solve the stated problem?
□ Is the approach sound? (No obvious bugs)
□ Is documentation clear? (Could a beginner use it?)
□ Are edge cases handled?
□ Is it genuinely valuable? (Not just "AI generated")
□ Does it match the request? (No scope drift)
```

### For Trinity Council
- DHARMIC_CLAW reviews Agni's work
- Agni reviews DHARMIC_CLAW's work
- RUSHABDEV (when joined) breaks ties
- Dhyana has veto power

**Output:** `layer2_review_approval.json`
**Fail Action:** Revise → Back to Layer 1 → Layer 2
**Pass Action:** Proceed to Layer 3

---

## LAYER 3: STAGING VALIDATION (Production Mirror)
**Gatekeeper:** Staging environment + 24-hour hold
**Time:** 1-24 hours
**Pass Criteria:** Real-world test successful

### Staging Process
```
1. Deploy to staging (not production)
2. Run for 24 hours (or minimum 1 hour for urgent)
3. Monitor: logs, errors, performance
4. User acceptance test (if applicable)
5. Final sign-off
```

### Staging Locations
- **Code:** Branch deployment, GitHub releases (draft)
- **Content:** Private gist, Notion (not public), Google Docs (comment mode)
- **Skills:** Local install, test environment (not ClawHub yet)
- **Products:** Beta users, waitlist only

### The 24-Hour Rule
**Hard constraint:** No publication within 24 hours of "complete"
**Why:** Prevents "done at 3am, published at 3:01am" mistakes
**Exception:** Hotfix for production outage (rare)

**Output:** `layer3_staging_signoff.json`
**Fail Action:** Fix → Back to appropriate layer
**Pass Action:** **SHIP TO PRODUCTION**

---

## SHIP CEREMONY

Only after all 3 layers:
```
1. Final git commit: "SHIP: [description] (3-layer validated)"
2. Tag version
3. Publish to production
4. Announce (if applicable)
5. Monitor for 48 hours
```

---

## ANTI-SLOP MANIFESTO

**What is AI Slop?**
- Code that "works" but is unmaintainable
- Content that reads as "generated" not "crafted"
- Products that exist but don't solve real problems
- Documentation that is complete but unusable

**How This Protocol Prevents It:**
- Layer 1 catches technical errors
- Layer 2 catches conceptual errors
- Layer 3 catches real-world failures
- 24-hour hold prevents emotional/decision fatigue

**The Toyota Connection:**
- Andon cord: Anyone can stop the line (veto)
- Jidoka: Automation with human judgment
- Kaizen: Continuous improvement (protocol iterates)
- Genchi Genbutsu: Go see the actual thing (Layer 3)

---

## PROTOTYPE REQUEST FOR AGNI

**Dhyana asks:**
1. Review this protocol
2. Implement automated Layer 1 checks (scripts)
3. Create staging environment setup
4. Build validation pipeline
5. Test on a real deliverable

**Success Criteria:**
- One deliverable passes all 3 layers
- Time from "done" to "shipped" > 24 hours
- Zero "AI slop" escapes

---

*Protocol v1.0 — Awaiting AGNI prototype*
