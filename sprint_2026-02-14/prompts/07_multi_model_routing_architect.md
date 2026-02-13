---
prompt_id: 07
name: Multi-Model Routing Architect
category: model_routing
version: 1.0
status: pending
agents_required:
  - rv_research_executor
  - code_security_reviewer
priority: P0
dependencies:
  - prompt_06
---

# Prompt 7: Multi-Model Routing Architect

You are the "Multi-Model Routing Architect" for a swarm that uses multiple LLMs (open + closed) without tunnel vision.

## GOAL (hard)
Specify a routing and arbitration system that:
- picks the cheapest sufficient model for each subtask
- detects when a model is out of its depth
- uses disagreement productively (not endlessly)
- enforces strict cost/latency budgets
- records everything as WitnessEvents with replayability

Assume models differ in: reasoning strength, tool calling reliability, safety behavior, latency, cost, and availability.

## OUTPUT (strict)
Return ONLY markdown with these sections in order:

### 1) ## Model Capability Taxonomy
Define capability tags (at least 12) such as:
- TOOL_CALLING_STRICT, LONG_CONTEXT, FORMAL_MATH, CODE_PATCHING, RETRIEVAL_QA, POLICY_REASONING, etc.

For each tag: definition + how to measure it (bench or harness).

### 2) ## Routing Policy
Define a deterministic routing algorithm:
Inputs: task type, risk tier, budget, required tags, current model health, and confidence requirements.
Outputs: selected model(s) + required verification steps.

Provide pseudo-code and explain key decisions.

### 3) ## Budget Enforcement
Define:
- per-task token and $ budgets
- per-interaction latency budgets
- "stop conditions" (abort, degrade, or escalate)

Include measurable rules and how they're logged.

### 4) ## Disagreement Protocol
Define a strict protocol for handling disagreement:
- when to trigger second/third opinions
- how to compare outputs (structured diff)
- when to escalate to verification lane or human review
- maximum rounds to avoid infinite loops

Provide a worked example with three hypothetical models.

### 5) ## Model Health Monitoring
Define:
- health metrics (latency, error rates, drift indicators, refusal patterns)
- how health affects routing
- canary tests that run periodically

Include thresholds and response actions (disable model, reduce scope, etc.).

### 6) ## Arbitration Outputs & Provenance
Define what artifacts must be produced for any arbitrated decision:
- candidate outputs
- decision rationale (structured)
- evidence links
- verification requirements
- final chosen output

All must be logged via WitnessEvents.

### 7) ## Failure Modes & Tests
List 20 failure modes (one line each) and for each:
- detection signal
- mitigation
- test case that proves your mitigation works

## HARD RULES
- Deterministic policies > vague "judge" prompts.
- Use "UNCERTAIN" as an explicit state that triggers verification, not handwaving.
- Never allow endless debate loops; enforce hard caps.
- Everything must map to measurable checks or logs.

Now produce the full spec.
