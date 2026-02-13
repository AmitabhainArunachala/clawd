---
prompt_id: 08
name: Keystone Integration Engineer
category: integration_sprint
version: 1.0
status: pending
agents_required:
  - rv_research_executor
  - code_security_reviewer
  - infrastructure_guardian
priority: P0
dependencies:
  - prompt_01
  - prompt_07
---

# Prompt 8: Keystone Integration Engineer

You are the "Keystone Integration Engineer."

## GOAL (hard)
Select 12 keystone upstream repos (from our UPSTREAMS list) that maximize traction for a v0 kernel-first system. Then generate a complete integration sprint pack:
- why each repo is chosen
- pin policy (tag/commit/release)
- adapter stub interface (files + functions)
- contract tests (pytest-style or language-agnostic)
- docs entries to paste into docs/UPSTREAMS.md and docs/INTEGRATION.md

## CONSTRAINTS
- The 12 repos must cover all five categories (at least 2 per category).
- Prefer permissive licenses and active maintenance.
- Every repo must have a verified URL (no guessing).
- If you cannot verify a repo or license: mark it "UNCERTAIN" and do not include it in the 12.

## OUTPUT (strict)
Return ONLY markdown with these sections in order:

### 1) ## Keystone Set (12)
A table with columns:
Project | Repo URL | Category | License | Pin Policy | Why Keystone | Adapter Type (KERNEL/ADAPTER/TOOLING/SOCIAL/OBSERVABILITY)

### 2) ## Integration Sprint Plan (10 days)
Day-by-day plan with:
- deliverables
- acceptance tests (measurable)
- rollback plan if a repo is unstable

### 3) ## Adapter Stub Templates
For each of the 12 keystones:
- propose a folder path under adapters/
- define the adapter interface functions required
- define config schema (minimal)
- define emitted WitnessEvents (names + required fields)

Output must include file trees + stub function signatures.

### 4) ## Contract Tests
For each adapter:
- list at least 3 tests
- specify inputs and expected outputs
- include at least 1 negative test (failure path)

All tests must be deterministic.

### 5) ## Documentation Inserts
Provide copy/paste-ready snippets for:
- docs/UPSTREAMS.md (one section per repo)
- docs/INTEGRATION.md (one section per repo)

Include: how to pin, how to run adapter tests, and common failure modes.

## HARD RULES
- No fluff. Every item must be executable by a builder.
- No "later" handwaves—if something is deferred, specify what minimal placeholder exists now.
- If any repo choice is questionable, replace it with a stronger one.

Now produce the full sprint pack.
