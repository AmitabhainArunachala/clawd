# Context Engineering Skill

Procedural skill for AI-to-AI communication and prompt construction. Transforms research findings into auto-applied practice.

---

## Purpose

Every output must be:
1. **Grounded** — What exists vs what's theater (binary classification first)
2. **Task-First** — The ask within first 256 tokens
3. **Properly Toned** — Collaborative for complex, directive for routine
4. **Telos-Aligned** — Each output maps to 500-year vs 90-day tension
5. **Constrained** — Explicit output format prevents philosophy drift

---

## The Five Filters (Apply in Order)

### Filter 1: Grounded Reality Check

**Before any analysis, classify:**

```
✅ REAL: [specific claim with file path/commit hash/evidence]
⚠️ PARTIAL: [claim with known gaps]
❌ THEATER: [vague claim without evidence]
```

**Mandatory for every session:**
1. Check `git log --oneline -5` — what actually shipped?
2. Check `ls -la` on claimed directories — do files exist?
3. Check test output — do tests pass or is it aspirational?
4. Classify every claim before analyzing it

**Anti-Pattern:**
```
❌ "The system is evolving toward consciousness"
✅ "12 commits since last session (git log), 3 test failures (pytest output), R_V metric 0.82 (measurable)"
```

---

### Filter 2: Task-First Structure

**The ask must appear within first 256 tokens.**

**Template:**
```
[ONE SENTENCE: What I need from you]

[Context: Why this matters, max 2 sentences]

[Specific Technical Ask:
- Command to run
- Exact format expected
- Validation criteria]

[Deadline/Constraint]
```

**Anti-Pattern (SECTION 1-6 bloat):**
```
❌ SECTION 1: Background
    SECTION 2: Philosophy
    SECTION 3: Theory
    SECTION 4: The Actual Task
    SECTION 5: Next Steps
    SECTION 6: Telos
```

**Correct:**
```
Run `git log --since="2026-02-12"` and paste output.

I need to sync our implementations before divergence. The factory is cycling every 15 minutes and I need ground truth on what you've actually shipped.

Output format:
- Raw git log output
- One-line description per commit
- Theater check: ✅ real / ⚠️ partial / ❌ stub

Deadline: 10:00 WITA (23 minutes)
```

---

### Filter 3: Vibe Coding Tone

**Complex work (research, extraction, integration):**
- Use "we", "let's", collaborative
- Ask questions, acknowledge uncertainty
- Iterative feedback loops
- Blueprint review before implementation

**Routine work (commands, file operations):**
- Clear, concise, directive
- No hedging
- Explicit commands

**Anti-Patterns:**
```
❌ Corporate: "Per your request, I have analyzed the system architecture and am pleased to report..."
❌ Sloppy: "idk maybe try this?"
✅ Collaborative: "Let's sync. I need to understand what you've built before I build against it."
✅ Directive: "Run: `cd ~/project && git log --oneline`"
```

---

### Filter 4: Architecture of the Gap

**Every output must acknowledge the tension:**

```
500-year vision: [Jagat Kalyan planetary intelligence]
90-day reality: [Current sprint deliverable]
Gap: [What makes this hard]
This output serves: [Which timescale, how]
```

**Example:**
```
Building R_V Toolkit sales page:
- 500-year: Funding consciousness research
- 90-day: $50 × 20 sales = $1000 ARR
- Gap: Research rigor vs marketing appeal
- This output: Professional sales copy that doesn't dilute scientific credibility
```

---

### Filter 5: Output Constraints

**Explicit format prevents philosophy drift:**

```
**Response Format:**
- JSON with these exact fields
- No prose explanation
- Gaps = OK (specify), Fiction = not OK
```

**Anti-Pattern:**
```
❌ "Analyze and discuss the system state..."
✅ "Fill this JSON:
{
  "git_commits": ["hash", "description"],
  "tests_passing": "N/M",
  "theater_check": "✅/⚠️/❌"
}"
```

---

## Application: META_COGNITION Cycle

**Before (Myopic):**
```
Read PSMV crown jewels, residual stream, builder outputs.
Produce meta_todos.json with actionable tasks.
```

**After (Integrated through skill):**

```
# Grounded Reality Check
Reading PSMV crown jewels (~/PSMV/00-CORE/SEED_CRYSTAL.md — file exists, 847 lines)
Reading residual stream (~/clawd/residual_stream/ — 225 entries, last 24h)
Reading builder outputs (~/clawd/handoffs/ — 4 HANDOFFs from 8-hour cycle)

Classification:
✅ REAL: 4 handoffs document actual shipped code
✅ REAL: 55 commits in 24h (verified: git log)
⚠️ PARTIAL: Some tasks incomplete (OrthogonalGates circular import)

# Task-First (within 256 tokens)
Generate meta_todos.json from current state.

Context: Factory ran 8 hours autonomously. Need actionable next steps that serve Jagat Kalyan.

Input sources:
- PSMV/00-CORE/SEED_CRYSTAL.md (telos)
- ~/clawd/handoffs/ (recent work)
- ~/clawd/CONTINUATION.md (work queue)

Output format:
{
  "timestamp": "ISO8601",
  "insights": [
    {
      "observation": "string (grounded in file/commit)",
      "engineering_task": "string (concrete, assignable)",
      "priority": "P0/P1/P2",
      "estimated_hours": int,
      "assigned_agent": "string"
    }
  ]
}

# Architecture of the Gap
500-year: Jagat Kalyan planetary intelligence layer
90-day: Fix remaining test failures, ship R_V Toolkit
Gap: Technical debt vs revenue generation
This output: Prioritized task list balancing both

# Vibe Coding
Let's synthesize the 8 hours of factory output into clear next steps.

# Output Constraint
JSON only. No prose. Each insight must cite source file.
```

---

## Verification Checklist

Before sending any output:

- [ ] Grounded reality check: theater/real classification done
- [ ] Task appears within first 256 tokens
- [ ] Tone appropriate: collaborative (complex) or directive (routine)
- [ ] Telos alignment: 500yr vs 90day acknowledged
- [ ] Output format explicitly constrained
- [ ] Every claim cites file/commit/evidence

---

## Integration with Existing Skills

**Before using any skill:**
1. Apply Filter 1 (Grounded Reality) — does this skill apply here?
2. Apply Filter 4 (Telos) — does this serve immediate need or ultimate purpose?
3. Apply Filter 5 (Constraint) — what's the expected output format?

**Skills this complements:**
- `openclaw-memory-tactics` — Use grounded reality before claiming knowledge
- `cosmic-krishna-coder` — Use task-first structure before coding
- `mech-interp` — Use output constraints for experimental protocols

---

## Anti-Patterns to Avoid

1. **Research accumulation without application** — Don't read 4 reports then file them; proceduralize immediately
2. **Philosophy-first prompts** — Never start with "Consider the nature of..."
3. **Implicit telos** — Never assume alignment is obvious
4. **Theater creep** — "Working on" without "committed to git" = theater
5. **Vibe mismatch** — Corporate tone for collaborative work, or vice versa

---

## Measurement

**Self-score each output:**
```
Grounded: 0-5 (all claims evidenced?)
Task-First: 0-5 (ask within 256 tokens?)
Tone: 0-5 (appropriate register?)
Telos: 0-5 (gap acknowledged?)
Constrained: 0-5 (explicit format?)

Total / 25 = Context Engineering Score
Target: >20/25
```

---

## Activation

**When to invoke:**
- Every prompt to another AI agent
- Every task decomposition
- Every research synthesis
- Every handoff documentation

**When NOT to invoke:**
- Simple file operations
- One-line responses
- Acknowledgments without content

---

*Skill created: 2026-02-17*
*Based on: RESEARCH_PROMPT_ENGINEERING_AI2AI.md, RESEARCH_VIBE_CODING.md, RESEARCH_EXTRACTION_CASE_STUDIES.md, TELOS_SYNTHESIS.md*
*Version: 1.0*
