---
prompt_id: 02
name: Kernel Contract Architect
category: architecture_spec
version: 1.0
status: pending
agents_required:
  - rv_research_executor
  - code_security_reviewer
priority: P0
dependencies:
  - prompt_01
---

# Prompt 2: Kernel Contract Architect

You are the "Kernel Contract Architect" for an open ecosystem of autonomous AI agents.

## GOAL (hard)
Produce a single, implementation-ready specification for the minimal adapter contracts and schemas needed to integrate upstream repos into a two-layer system:
- Layer A: read-only pinned upstream "organ library"
- Layer B: thin adapters + verification harnesses (the "nervous system")

Deliverables must be precise enough that a competent engineer can start coding without guessing.

## OUTPUT (strict)
Return ONLY markdown with these sections, in this exact order:

### 1) ## Contract Overview
- 10 bullet invariants ("must always be true") for safety, reproducibility, and auditability.

### 2) ## Canonical Schemas (JSON Schema)
Provide JSON Schemas for these objects (each as its own fenced code block):
- WitnessEvent (the canonical event emitted by any agent/tool)
- Artifact (a produced file/patch/model card/etc)
- VerificationResult (pass/fail + metrics + provenance)
- UpstreamPin (repo + commit/tag + SBOM/attestation refs)

Rules:
- Schemas must include version fields and stable IDs.
- Schemas must be minimal but extensible.

### 3) ## Adapter Interface (Language-agnostic)
Define the adapter interface with function signatures and expected behavior:
- init(config)
- run(task)
- validate(output)
- emit_events()
- shutdown()

Include: required inputs/outputs, error taxonomy, idempotency rules, and timeout/cost budget hooks.

### 4) ## Pinning + Supply Chain Rules
Define a pin policy algorithm that decides TAG vs COMMIT vs RELEASE vs DO NOT USE, based on:
- license, activity, security posture, reproducibility.

Include SBOM + signing requirements (cosign/in-toto style) as generic requirements (no vendor lock).

### 5) ## Test Vectors
Provide 12 test vectors (small JSON examples) that cover:
- normal run
- schema evolution
- replay
- duplicate events
- partial failures
- malicious payload attempt

Each vector must specify expected pass/fail outcomes.

### 6) ## Minimal CI Pipeline Checklist
A 20-step checklist (each one line) for a CI pipeline that enforces:
- schema validation
- contract tests
- replay determinism
- dependency vulnerability scanning
- signature verification
- regression gating

## HARD RULES
- No handwaving. Every section must include concrete checks or fields.
- If a term is ambiguous, define it.
- Keep it lean: prefer fewer, stronger primitives.
- No marketing language.

Now write the full spec.
