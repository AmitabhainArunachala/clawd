---
prompt_id: 06
name: Lead Architect + Program Manager
category: implementation_plan
version: 1.0
status: pending
agents_required:
  - rv_research_executor
  - code_security_reviewer
  - infrastructure_guardian
priority: P0
dependencies:
  - prompt_05
---

# Prompt 6: Lead Architect + Program Manager

You are the "Lead Architect + Program Manager" for building a kernel-first, integrity-preserving agent ecosystem.

## GOAL (hard)
Produce a concrete implementation plan that a small team (or one strong solo builder) can execute in 30 days to reach a credible v0 that:
- runs a minimal swarm
- produces WitnessEvents
- stores artifacts
- verifies at least 10 evals end-to-end
- integrates a basic social layer (even if minimal UI)
- has pinning + supply-chain hygiene from day 1

## OUTPUT (strict)
Return ONLY markdown with these sections in order:

### 1) ## Repo Layout (Monorepo)
Propose a monorepo structure with folders and short descriptions. Must include:
- kernel/ (schemas, invariants, policy, witness event)
- adapters/ (provider + tool adapters)
- verification/ (eval harness)
- sandbox/ (tool runner)
- social/ (API + minimal web)
- infra/ (deploy, secrets, observability)
- docs/ (UPSTREAMS, CONTRIBUTING, GOVERNANCE)
- examples/ (end-to-end demos)

Include naming conventions and versioning strategy.

### 2) ## Milestones (7-day increments)
Define 4 weekly milestones (Week 1–4). Each milestone must list:
- deliverables
- acceptance tests (measurable)
- cut scope if behind schedule (explicit "drop list")

### 3) ## v0 Feature Set (Non-Negotiables)
List exactly 15 features that v0 must have, each with:
- why it matters
- test that proves it works

### 4) ## First 10 Evals
Define 10 evals that demonstrate integrity and traction:
- 3 deterministic unit tests
- 3 adversarial/injection tests
- 2 retrieval tests
- 2 social/governance tests

For each eval: goal, procedure, pass/fail thresholds, required artifacts.

### 5) ## Minimal Deployment Plan
Give a step-by-step deployment plan for:
- local dev
- single VPS (Docker compose)
- optional k8s later

Include secrets handling and observability hooks.

### 6) ## Risk Register
List 15 risks with:
- severity (H/M/L)
- likelihood (H/M/L)
- mitigation (concrete)
- early warning signal (metric or log)

## HARD RULES
- Everything must have acceptance tests.
- Keep scope minimal: v0 should be shippable by a solo builder.
- Prioritize "auditability + reproducibility" over "features."

Now produce the plan.
