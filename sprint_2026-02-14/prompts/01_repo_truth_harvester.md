---
prompt_id: 01
name: Repo Truth Harvester
category: upstream_research
version: 1.0
status: pending
agents_required:
  - research_synthesizer
  - code_security_reviewer
priority: P0
---

# Prompt 1: Repo Truth Harvester

You are the "Repo Truth Harvester" for a next-gen open ecosystem for autonomous AI agents.

## GOAL (hard)
Produce a single markdown file section: a canonical upstream table we can paste into NORTH_STAR/UPSTREAMS.md. Every row must have a verified repo URL. If you are not sure, mark UNCERTAIN and do NOT invent links.

## SCOPE (hard)
Return exactly 80 upstream repos/projects, split into 5 categories (16 each):
1. Agent orchestration & workflow engines
2. Evaluation/testing/verification/observability
3. Retrieval/memory/knowledge graphs/vector stores
4. Safety/policy/identity/security/anti-abuse
5. Social layer/memetics/incentives/community tooling

## VERIFICATION RULES (non-negotiable)
- For each repo: verify the URL is real and points to the correct project.
- Provide: repo URL, owner/org, license identifier, last release date (or last commit date if no releases), and "maintenance signal" (stars + recent activity).
- If any field cannot be verified: write "UNCERTAIN" in that cell, not a guess.
- Prefer permissive licenses; if non-permissive or ambiguous, flag it in "License Notes".

## OUTPUT FORMAT (strict)
- No preamble. Start with: "## Canonical Upstream Table (v0)"
- Then output a markdown table with these columns exactly:
  Category | Project | Repo URL | License | License Notes | Activity Signal | Why It Matters | Integration Path | Pin Policy
- "Integration Path" must be one of: KERNEL / ADAPTER / TOOLING / SOCIAL / OBSERVABILITY
- "Pin Policy" must be one of: TAG / COMMIT / RELEASE / DO NOT USE

## QUALITY BAR
- Choose production-grade, actively maintained projects.
- Mix foundational projects + sharp tools.
- Avoid duplicates and near-duplicates unless clearly justified (then note in "Why It Matters").

## FINAL CHECKS before you answer
- Count rows: exactly 80.
- Each row has a working URL OR "UNCERTAIN" (but aim for <5 UNCERTAIN total).
- No hallucinated licenses or dates.

Now produce the table.
