---
prompt_id: 09
name: Truth Data Model Architect
category: data_model
version: 1.0
status: pending
agents_required:
  - rv_research_executor
  - code_security_reviewer
  - memory_pattern_curator
priority: P0
dependencies:
  - prompt_08
---

# Prompt 9: Truth Data Model Architect

You are the "Truth Data Model Architect" for a verification-driven knowledge ecosystem.

## GOAL (hard)
Specify the data model that allows the platform to store and query:
- claims
- evidence
- provenance
- verification results
- relationships between claims (dependencies, contradictions, refinements)
- staleness and update cycles

…and do it in a way that is auditable and supports retrieval without becoming a hallucination amplifier.

You must define both:
A) the logical model (entities + relations)
B) a practical storage plan (Postgres-first; optional graph/vector add-ons)

## OUTPUT (strict)
Return ONLY markdown with these sections in order:

### 1) ## Core Concepts (Precise Definitions)
Define: Claim, Evidence, Source, Artifact, VerificationResult, CanonicalEntry, Contradiction, Revision, Staleness, TrustScore.

Each definition must include: required fields and what it is NOT.

### 2) ## Entity-Relationship Model
List entities and relations (in bullet form) including cardinalities. Must include:
- Claim ↔ Evidence
- Claim ↔ Claim (supports/contradicts/refines/depends_on)
- Claim ↔ VerificationResult
- CanonicalEntry ↔ Claim (what becomes canonical and why)

### 3) ## Canonicalization Protocol
Define how something becomes canonical:
- stages
- required verification classes
- citation/provenance requirements
- how revisions happen (no silent edits)
- how retractions work

Include explicit pass/fail criteria and required logs.

### 4) ## Staleness Control
Define:
- TTL policies by domain/risk
- refresh triggers (time, disagreement, external change)
- what happens when TTL expires (downgrade, quarantine, re-verify)

Include a "staleness score" formula.

### 5) ## Storage Plan (Postgres-first)
Propose:
- table schemas (high-level fields)
- indexes
- partitioning for event logs
- how to store artifacts (object store + hashes)
- how to integrate vectors (pgvector or external)
- optional graph DB integration (only if needed)

Keep it minimal and implementable.

### 6) ## Query Patterns
Provide 12 query patterns (natural language + what it should return), e.g.:
- "Show me the strongest evidence for claim X"
- "What claims become invalid if source Y is retracted?"
- "List contradictions in topic T"
- "Show stale canonical entries"

For each: required joins/indices (high-level).

### 7) ## Integrity Tests
Provide 20 integrity tests (one line each) that validate:
- provenance completeness
- no orphan evidence
- no silent edits
- contradiction handling
- TTL behavior

Each test must have expected pass/fail behavior.

## HARD RULES
- Assume adversaries will try to launder fake sources and inject prompt instructions into evidence.
- The model must support "UNCERTAIN" as a state and quarantine.
- No big-bang graph DB. Start Postgres-first and justify any add-on.

Now write the full spec.
