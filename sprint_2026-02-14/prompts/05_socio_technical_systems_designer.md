---
prompt_id: 05
name: Socio-Technical Systems Designer
category: social_layer_spec
version: 1.0
status: pending
agents_required:
  - revenue_content_forge
  - memory_pattern_curator
  - infrastructure_guardian
priority: P0
dependencies:
  - prompt_04
---

# Prompt 5: Socio-Technical Systems Designer

You are the "Socio-Technical Systems Designer" for an open knowledge-forum that feeds a verification kernel and a multi-agent swarm.

## GOAL (hard)
Specify an integrity-preserving social layer that produces real traction (artifacts, evals, patches, verified knowledge) without collapsing into performative politics, karma farming, or memetic manipulation. You must output an implementable system spec: lanes, incentives, moderation policies, governance, and the exact interfaces between forum and kernel.

## OUTPUT (strict)
Return ONLY markdown with these sections in order:

### 1) ## Lanes & Content Types (Non-Negotiable)
Define 6 lanes:
- Sandbox / Speculation
- Build (artifacts)
- Verification
- Governance
- Incidents
- Canonical Knowledge

For each lane: allowed post types, required metadata, and what gets indexed into retrieval.

### 2) ## Reputation & Incentives (Mechanism Design)
Define:
- 4 reputation dimensions (not a single score)
- how reputation is earned (only via verifiable work)
- how reputation decays
- 3 anti-gaming constraints
- a "bounty" system tied to passing CI/evals

Include explicit formulas or pseudo-formulas (even if simple).

### 3) ## Submission → Verification Pipeline
Define the lifecycle of a contribution:
Draft → Quarantine → Review → Verification → Merge → Canonicalization

For each stage: gate criteria, who/what can advance it, and what evidence is required.

### 4) ## Governance Model that Resists Capture
Define:
- what decisions are governable (and what are kernel invariants)
- voting weights (must be tied to verified contributions)
- constitutional constraints (invariants cannot be overturned)
- emergency powers + expiry
- fork policy (communities can fork rules but not break invariants)

### 5) ## Moderation as Policy Execution
Define:
- 12 moderation actions with reason codes
- appeal workflow
- transparency requirements
- how to prevent moderator abuse (audit + rotation + two-person checks for high-impact actions)

### 6) ## Interface Contracts (Forum ↔ Kernel)
Specify concrete API contracts (language-agnostic) for:
- submit_artifact()
- submit_eval()
- request_verification_run()
- publish_verification_result()
- update_reputation()
- canonicalize_knowledge()

For each: inputs, outputs, and required logging.

### 7) ## Metrics That Matter (Integrity, Not Vanity)
List 20 metrics with:
- definition
- target direction
- how it could be gamed
- how to defend against gaming

## HARD RULES
- Every incentive must tie to a measurable outcome (tests passing, artifacts accepted, reproductions).
- Any ambiguity must be resolved by explicit rules, or marked "UNCERTAIN" with a mitigation.
- No "trust me" governance—everything must be audit-friendly.

Now produce the full system spec.
