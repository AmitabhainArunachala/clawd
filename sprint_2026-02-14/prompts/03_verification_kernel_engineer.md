---
prompt_id: 03
name: Verification Kernel Engineer
category: verification_architecture
version: 1.0
status: pending
agents_required:
  - rv_research_executor
  - code_security_reviewer
  - memory_pattern_curator
priority: P0
dependencies:
  - prompt_02
---

# Prompt 3: Verification Kernel Engineer

You are the "Verification Kernel Engineer" for a large-scale agent ecosystem.

## GOAL (hard)
Define a verification system that makes outputs auditable, reproducible, and hard to game. You must propose a concrete architecture for evaluations, including measurable pass/fail criteria, and how it plugs into the agent swarm.

## OUTPUT (strict)
Return ONLY markdown with the following sections in order:

### 1) ## Verification Kernel: Purpose + Non-Goals
- 5 bullets for purpose
- 5 bullets for explicit non-goals (what this system will NOT attempt)

### 2) ## Verification Taxonomy
Define 6 verification classes, each with:
- name
- what it verifies
- typical failure modes
- required evidence artifacts

Example classes should include: deterministic tests, property-based tests, differential checks, provenance checks, sandbox policy checks, and "human spot-check" integration.

### 3) ## The "Pass/Fail Contract"
Define a universal contract that every verification must implement:
- Inputs
- Outputs
- Metrics
- Thresholds
- Confidence handling
- How to handle "UNCERTAIN"

Include a strict rule for when uncertainty is allowed vs when it blocks merging.

### 4) ## Evaluation Suite Architecture
Define how evals are organized and executed:
- folder/module layout
- naming conventions
- how to register a new eval
- how to version datasets
- how to run locally vs CI
- how to store artifacts and logs

Include a minimal example of an eval definition (pseudo-code OK).

### 5) ## Anti-Gaming Defenses
Provide 12 concrete anti-gaming mechanisms, each with:
- attack it prevents
- how it detects/prevents it
- measurable test for the defense itself

Include things like train/test separation, canary evals, adversarial perturbations, leakage detection, and multi-model cross-checks.

### 6) ## CI Gates + Release Gates
Define:
- what runs on every PR (fast suite)
- what runs nightly (full suite)
- what runs before release (certification suite)

Each gate must include target runtimes and explicit pass thresholds.

### 7) ## Minimal Metrics Dashboard
List 15 metrics you would track (one line each) that actually matter for truth/integrity (not vanity). For each metric: definition + why it matters.

## HARD RULES
- Every proposal must include a measurable pass/fail definition.
- Avoid reliance on subjective "LLM judging" unless it is anchored to explicit rubrics and spot checks.
- No vague phrases like "robust," "better," "high quality" without operationalization.

Now produce the full architecture.
