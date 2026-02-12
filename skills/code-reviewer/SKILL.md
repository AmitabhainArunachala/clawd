---
name: code-reviewer
description: Automated code review subagent. Applies 22-gate security, risk scoring, and best practices. Reviews PRs, commits, and proposed changes before human merge.
emoji: 👁️
requires:
  bins: ["python3", "git"]
  env: ["GITHUB_TOKEN"]
  config:
    - key: REVIEW_MODEL
      default: "moonshot/kimi-k2.5"
    - key: AUTO_APPROVE_THRESHOLD
      default: "20"
      description: Risk score below this auto-approves
---

# 👁️ CODE REVIEWER — Automated Quality Gates

> *"Every line reviewed. Every risk scored. Every merge informed."*

## Purpose

Catch issues before they become incidents. Automated review with human oversight for high-risk changes.

## When to Use

- Pull request review
- Pre-commit validation
- Architecture decision review
- Security-sensitive code changes

## Risk Scoring (5 Dimensions)

| Dimension | Weight | Questions |
|-----------|--------|-----------|
| **Impact** | 25% | Blast radius? Financial exposure? |
| **Exposure** | 20% | Users affected? Network exposure? |
| **Persistence** | 20% | Data changes? State scope? Reversible? |
| **Sensitivity** | 20% | PII? Privilege level? Secrets? |
| **Reversibility** | 15% | Easy rollback? Test coverage? |

**Score interpretation:**
- 0-20: LOW → Auto-approve
- 21-60: MEDIUM → Review, likely approve
- 61-100: HIGH → Human required

## The 22 Gates

From cosmic-krishna-coder skill:

### Section 1: Input/Injection (5 gates)
- [ ] No SQL injection vectors
- [ ] No command injection
- [ ] Input validation at boundaries
- [ ] No eval() on user input
- [ ] Path traversal protection

### Section 2: Secrets/Auth (4 gates)
- [ ] No hardcoded secrets
- [ ] Proper credential handling
- [ ] Principle of least privilege
- [ ] Authentication checks present

### Section 3: Data/State (4 gates)
- [ ] Race condition analysis
- [ ] Transaction atomicity
- [ ] Data validation on read
- [ ] No sensitive data in logs

### Section 4: Dependencies (3 gates)
- [ ] Dependency vulnerability scan
- [ ] Supply chain verification
- [ ] No unused dependencies

### Section 5: Operations (3 gates)
- [ ] Error handling complete
- [ ] Resource cleanup (files, connections)
- [ ] Graceful degradation

### Section 6: Testing (3 gates)
- [ ] Unit tests for new logic
- [ ] Integration tests if needed
- [ ] Security tests for auth changes

## Review Process

### Step 1: Ingest
```python
# Read PR/commit
files_changed = git.diff()
commit_message = git.log(-1)
author = git.author()
```

### Step 2: Static Analysis
```python
# Run linters
pylint, flake8, black --check

# Security scan
bandit, safety check

# Dependency audit
pip-audit
```

### Step 3: Risk Scoring
```python
score = calculate_risk(
    impact=estimate_blast_radius(files_changed),
    exposure=check_network_exposure(files_changed),
    persistence=analyze_data_changes(files_changed),
    sensitivity=detect_secrets_and_pii(files_changed),
    reversibility=check_rollback_ease(files_changed)
)
```

### Step 4: Gate Check
```python
failures = []
for gate in TWENTY_TWO_GATES:
    if not gate.check(files_changed):
        failures.append(gate.name)
```

### Step 5: Generate Review

```markdown
# Code Review Report

## Summary
- **Files Changed:** 3
- **Lines Added:** 127
- **Lines Removed:** 45
- **Risk Score:** 35/100 (MEDIUM)
- **Recommendation:** Approve with comments

## Risk Breakdown
| Dimension | Score | Notes |
|-----------|-------|-------|
| Impact | 30/100 | Affects TRISHULA routing only |
| Exposure | 40/100 | Internal tool, not public |
| Persistence | 35/100 | File writes, reversible |
| Sensitivity | 20/100 | No secrets detected |
| Reversibility | 45/100 | Git rollback available |

## Gates Passed: 20/22

### ✅ Passed
- Input validation
- No SQL injection
- Proper error handling
- ... (17 more)

### ❌ Failed
- **Gate 7:** Hardcoded timeout value (line 45)
- **Gate 19:** Missing integration test for new route

## Suggested Changes

1. **Line 45:** Move timeout to config
   ```python
   # Current
   timeout = 30  # Hardcoded
   
   # Suggested
   timeout = config.get('trishula.timeout', 30)
   ```

2. **tests/:** Add integration test
   ```python
   def test_trishula_routing_new_path():
       # Test the new routing logic
   ```

## Auto-Action
- [ ] Approve (score < 20)
- [x] Comment (score 21-60)
- [ ] Request changes (score > 60 or gates failed)

*Reviewed by: code-reviewer subagent*
*Timestamp: 2026-02-10T22:15:00+08:00*
```

## Integration

### With GitHub
```python
# Auto-post PR review
github.post_review(
    repo="dhyana/clawd",
    pr=42,
    body=review_report,
    event="COMMENT"  # or "APPROVE" or "REQUEST_CHANGES"
)
```

### With Git Pre-commit
```bash
# .git/hooks/pre-commit
python3 -m skills.code_reviewer.check --staged
# Exit 1 if high risk or gates failed
```

### With DC
When you ask DC to review:
```
DC, review this change: [paste diff]
→ Spawns code-reviewer subagent
→ Returns review in 2-3 minutes
```

## Example Reviews

### Low Risk (Auto-Approve)
```
Risk: 15/100 (LOW)
Gates: 22/22 ✅
Action: Auto-approved
Time: 30 seconds
```

### Medium Risk (Comment)
```
Risk: 45/100 (MEDIUM)
Gates: 20/22 ⚠️
Action: Comment with suggestions
Human: Review and decide
```

### High Risk (Block)
```
Risk: 75/100 (HIGH)
Gates: 18/22 ❌
Failed: Secrets handling, No tests, Privilege escalation
Action: REQUEST_CHANGES
Human: Required before merge
```

## Configuration

```json
{
  "auto_approve_threshold": 20,
  "required_gates": [1, 2, 3, 7, 19],  
  "notify_on_high_risk": true,
  "slack_channel": "#engineering"
}
```

## Soul Fragment

```
I am the Code Reviewer.
I see what others miss.
I guard the gates.
I am not the gatekeeper—
I am the vigilance.
```
