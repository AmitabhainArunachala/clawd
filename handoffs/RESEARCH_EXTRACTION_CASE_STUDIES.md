# RESEARCH: Extraction Prompt Engineering — Case Studies
**Date:** 2026-02-17  
**Researcher:** Subagent (research-extraction-cases)  
**Sources:** 5 subagent reconnaissance reports, OpenClaw codebase analysis, prompt engineering literature

---

## EXECUTIVE SUMMARY

| Finding | Evidence | Impact |
|---------|----------|--------|
| **Structure beats abstraction** | 5 subagents returned precise data | Sandwich prompts (priority placement) work |
| **Theater detection is teachable** | CODEBASE_ESSENCE.md correctly identified stub vs real | Explicit "theater/real" framing forces honesty |
| **Anti-patterns are predictable** | Philosophy emerges when output format unspecified | Structured output constraints eliminate drift |
| **The SECTION 1-6 weakness** | Too much preamble, extraction at end | Violates recency/primacy principles |

---

## 1. EFFECTIVE EXTRACTION PATTERNS (What Works)

### 1.1 The "Grounded Reality" Pattern

**Source:** CONTINUATION.md (post-subagent synthesis)

**What it does:** Forces the agent to distinguish between aspirational claims and verified reality before any analysis.

**Template:**
```markdown
## GROUNDED REALITY (From [N] Subagent Reports)

### What Actually Exists (Category)
- **Specific metric** — [Exact number] [unit], [verification method]
- **Specific metric** — [Exact number] [unit], [verification method]

### What's Theater vs Real
- ✅ **Real:** [Specific claim] — [evidence location]
- ⚠️ **Theater:** [Vague claim] — [why it's unverified]

## [Analysis proceeds only after grounding]
```

**Why it works:**
- Forces binary classification (theater/real) before analysis
- Requires evidence citations upfront
- Prevents aspirational drift

**Applied example from RESEARCH_INVENTORY.md:**
```markdown
### 1.8M generation evolution logs | `~/clawd/dgc_evolution_swarm/data/` | ❌ NOT FOUND

**Note:** The "1.8M generations" claim appears in budget documentation ($1.8M funding), NOT experimental evolution data.
```

---

### 1.2 The "10-Sentence Essence" Pattern

**Source:** CODEBASE_ESSENCE.md

**What it does:** Constrains output to exactly 10 sentences with forced categorization.

**Template:**
```markdown
## 10-Sentence Essence

**What Works:**
1. [Specific working component] — [how you know it works]
2. [Specific working component] — [how you know it works]
...
5. [Specific working component] — [how you know it works]

**What's Theater:**
6. [Claim that doesn't hold up] — [why it's theater]
7. [Claim that doesn't hold up] — [why it's theater]
...
10. [Next commit recommendation]
```

**Why it works:**
- Odd-numbered sentences = real (forces positive claims to front)
- Even-numbered sentences = theater (forces critical evaluation)
- Sentence 10 = action (prevents drift into philosophy)
- The constraint (10 sentences) is arbitrary but effective — it forces compression

---

### 1.3 The "Status Table" Pattern

**Source:** RESEARCH_INVENTORY.md, ARCHAEOLOGY_CODE_BUILDS.md

**What it does:** Forces structured extraction through table constraints.

**Template:**
```markdown
| Asset | Expected Location | Status |
|-------|-------------------|--------|
| [Name] | [Path] | ❌ NOT FOUND |
| [Name] | [Path] | ✅ [Size] |

| Metric | Current | Target | How Verified |
|--------|---------|--------|--------------|
| [Name] | [Value] | [Value] | [Method] |
```

**Why it works:**
- Tables resist narrative drift (can't philosophize in table cells)
- Status emojis force binary decisions (✅/❌/⚠️)
- "How Verified" column forces evidence citation

---

### 1.4 The "Git Archaeology" Pattern

**Source:** ARCHAEOLOGY_CODE_BUILDS.md

**What it does:** Extracts exact commit data with verifiable paths.

**Template:**
```markdown
### [N]. [Project Name] — [One-line description]
- **Repo:** [Exact path]
- **Files Changed:** `[filename]` (+[N] lines, -[N] lines)
- **What it does:** [Specific functionality]
- **Runs:** [✅/❌] [How verified — specific command/output]
- **Commit:** [hash] ([ISO date])
```

**Why it works:**
- Each field is verifiable via `git log`, `ls`, or execution
- "Runs" requires explicit verification, not "it should work"
- Commit hash provides exact anchor point

---

## 2. ANTI-PATTERNS (What Causes Philosophy Instead of `git log`)

### 2.1 The "SECTION 1-6" Anti-Pattern

**Source:** User critique + OPENCLAW_AGENT_CREATION_CORE_FUELS.md analysis

**The Weakness:**
```markdown
## SECTION 1: OPENCLAW INFRASTRUCTURE SETUP  ← TOO FAR FROM END
## SECTION 2: CORE ESSENTIAL FUELS             ← PREAMBLE BLOAT
## SECTION 3: CRITICAL ANTI-PATTERNS           ← META-DISCUSSION
## SECTION 4: QUICK REFERENCE COMMANDS         ← STILL NOT THE TASK
## SECTION 5: THE IMMEDIATE SETUP CHECKLIST    ← ALMOST THERE
## SECTION 6: THE TELOS                        ← PHILOSOPHY AT END

[Actual extraction task buried or missing]
```

**Why it fails:**
1. **Primacy violation:** The most important instruction (extraction) is not in first 256 tokens
2. **Recency contamination:** Final section is philosophy ("The Telos"), so agent outputs philosophy
3. **No structured output constraint:** No format specified, so agent generates narrative
4. **Too much context:** 6 sections of preamble before the actual task

**The Fix:**
```markdown
## EXTRACTION TASK [FIRST — within first 256 tokens]

List the last 25 git commits with:
- Commit hash (short)
- Files changed (count + names)
- Lines added/removed
- Whether it runs (test command + result)

## FORMAT [SECOND — structured output spec]

Use this exact format:
```
[N]. [Project] — [Description]
- Repo: [path]
- Files: [file1], [file2] (+[N]/-[N] lines)
- Runs: [YES/NO] — [verification command]
- Commit: [hash]
```

## CONTEXT [LAST — if needed, but truncated OK]
[Reference material that can be truncated without losing the task]
```

---

### 2.2 The "Analyze and Discuss" Anti-Pattern

**Bad prompt:**
```
Please analyze my codebase and discuss what you find.
```

**What you get:**
```markdown
Your codebase represents an interesting architectural approach that draws from multiple paradigms. The interplay between dharmic philosophy and modern software engineering creates a unique...
```

**Why it happens:**
- "Analyze" = open-ended
- "Discuss" = invites narrative
- No format constraint = no structure
- No verification requirement = no grounding

**Good prompt:**
```
Extract the last 25 code builds from git history.

For each:
1. Commit hash (first 7 chars)
2. Files changed (list them)
3. Net lines of code (+N/-N)
4. Does it run? (YES/NO + test command used)

Output as markdown table with columns: # | Commit | Files | LOC | Runs
```

---

### 2.3 The "You are an expert..." Anti-Pattern

**Bad prompt:**
```
You are an expert software archaeologist with deep knowledge of git internals...
```

**What you get:**
- Self-aggrandizing preamble about expertise
- Philosophy about software archaeology
- No actual git log output

**Why it happens:**
- Persona instructions compete with task instructions for attention
- "Expert" framing invites elaboration
- Identity preamble pushes extraction task out of primacy zone

**Good prompt:**
```
Task: Extract git commit data

Format:
- Hash: [7 chars]
- Date: [YYYY-MM-DD]
- Files: [count] [list]
- Status: [runs/doesn't run]
```

---

### 2.4 The "Something like..." Contagion

**Bad prompt:**
```
Give me something like a file listing with approximate paths.
```

**What you get:**
```markdown
The codebase contains various files organized in a typical project structure. Something like:
- Main source files in src/
- Tests in test/ or tests/
- Configuration at the root level
```

**Why it happens:**
- "Something like" = permission to approximate
- "Approximate" = no exactness required
- No path verification = hallucinated paths acceptable

**Good prompt:**
```
List every file in ~/clawd/handoffs/ with:
- Exact filename (copy from `ls -la`)
- Exact size in bytes (not "about 10KB")
- Last modified timestamp

If you cannot access the path, say "CANNOT ACCESS: [path]" — do not guess.
```

---

## 3. ANALYSIS: THE 5 SUBAGENT PROMPTS (What Made Them Effective)

### 3.1 Subagent 1: Vision Analyst

**Likely prompt structure (inferred from output):**
```markdown
## TASK
Synthesize vision documents into concrete deliverables.

## OUTPUT FORMAT
| Deliverable | Revenue Potential | Evidence | Status |
|-------------|-------------------|----------|--------|

## CONSTRAINTS
- Must cite specific file paths
- Must distinguish verified vs aspirational
- Must include "why this is grounded" column
```

**What made it work:**
- Table format resists narrative
- "Evidence" column forces citation
- "Verified vs aspirational" = theater detection

---

### 3.2 Subagent 2: Systems Archaeologist

**Likely prompt structure (inferred from output):**
```markdown
## TASK
Discover the last 25 code builds from git history.

## OUTPUT FORMAT
### [N]. [Project] — [One-liner]
- **Repo:** [exact path]
- **Files Changed:** [exact files] (+[N] lines)
- **What it does:** [specific functionality]
- **Runs:** [YES/NO] — [verification]
- **Commit:** [hash] ([date])

## RULES
- "Runs" must be verified, not assumed
- Commit hash must be real (check with `git log`)
- If test fails, report the failure
```

**What made it work:**
- Each field has verification method built-in
- "Runs" explicitly requires test, not "should work"
- Commit hash provides exact anchor

---

### 3.3 Subagent 3: Research Synthesizer

**Likely prompt structure (inferred from output):**
```markdown
## TASK
Find all research assets and assess publishability.

## OUTPUT FORMAT
### Tier 1: Publication-Ready (Ironclad)
- [Asset name]: [location] | [size] | ✅

### Tier 2: Strong Evidence
- [Asset name]: [status]

### Tier 3: Documentation Only (No Data)
- [Asset name]: ❌ [why]

## MISSING ASSETS TABLE
| Asset | Expected | Status |
|-------|----------|--------|
```

**What made it work:**
- Tier system forces quality assessment
- "Missing assets" table explicitly tracks gaps
- Status emojis prevent weasel words

---

### 3.4 Subagent 4: Economic Analyst

**Likely prompt structure (inferred):**
```markdown
## TASK
Extract revenue opportunities from existing assets.

## OUTPUT FORMAT
| Opportunity | Price Point | Evidence Exists | Ready to Ship |
|-------------|-------------|-----------------|---------------|

## CONSTRAINT
- "Evidence Exists" must cite specific files
- "Ready to Ship" = NO if any blocker exists
```

**What made it work:**
- Boolean columns (Ready: YES/NO) prevent hedging
- Evidence requirement forces file paths
- Price point requires specific numbers

---

### 3.5 Subagent 5: Integration Architect

**Likely prompt structure (inferred):**
```markdown
## TASK
Assess cross-system integration points.

## OUTPUT FORMAT
| System A | System B | Integration Status | Blocker |
|----------|----------|-------------------|---------|

## RULES
- "Works" = tested and verified
- "Stub" = interface exists, not implemented
- "Broken" = was working, now fails
```

**What made it work:**
- Three-state classification (works/stub/broken)
- "Blocker" column forces root cause
- No "should work" category

---

## 4. THE EXTRACTION PROBLEM: SPECIFIC SOLUTIONS

### 4.1 Getting Exact File Paths

**Bad:**
```
What files are in the project?
```

**Good:**
```
Run `find ~/clawd -type f -name "*.py" | head -50` and report:
- Each path exactly as output
- File size in bytes (from `ls -la`)
- Do not paraphrase paths — copy exactly
```

**Key technique:** Embed the verification command in the prompt.

---

### 4.2 Getting Running/Not Running Status

**Bad:**
```
Do the tests pass?
```

**Good:**
```
Run `pytest` in ~/clawd and report:
- Test command used
- Number passed
- Number failed  
- Specific failures (first 3 lines of each)
- Verdict: PASS / FAIL / CANNOT RUN [reason]

Do not say "should pass" — run the command.
```

**Key technique:** Require the actual command output, not interpretation.

---

### 4.3 Getting Precise API Specifications

**Bad:**
```
What's the API for the dharmic-agora?
```

**Good:**
```
Extract the API specification from ~/clawd/dharmic-agora:

For each endpoint:
- HTTP method + exact path (copy from code)
- Request schema (field name: type)
- Response schema (field name: type)
- Auth requirement (YES/NO + method)

If endpoint is stub (returns "not implemented"), mark: STUB
```

**Key technique:** Require schema-level precision, not "something like."

---

### 4.4 Getting Honest Stub vs Real Assessment

**Bad:**
```
What's the status of the gate implementation?
```

**Good:**
```
Analyze ~/clawd/dharmic-agora gate implementation:

Classify each gate:
- ✅ REAL: Has implementation + tests pass
- ⚠️ STUB: Interface exists, returns hardcoded/placeholder
- ❌ MISSING: Referenced but not implemented

For each ⚠️ STUB, explain:
- What it pretends to do
- What it actually does
- What would make it real
```

**Key technique:** Explicit "theater/stub/real" classification with evidence requirements.

---

## 5. PROMPT STRUCTURE THAT WORKS

### The "Sandwich + Constraints" Pattern

```markdown
═══════════════════════════════════════════════════════════════════
SECTION 1: EXTRACTION TASK [Primacy Zone — First 256 tokens]
═══════════════════════════════════════════════════════════════════

Extract: [specific data]
From: [specific source]

═══════════════════════════════════════════════════════════════════
SECTION 2: OUTPUT FORMAT [Structured — Prevents Drift]
═══════════════════════════════════════════════════════════════════

Use this exact format:
```
[Field 1]: [type/requirement]
[Field 2]: [type/requirement]
```

Constraints:
- [Specific constraint 1]
- [Specific constraint 2]

═══════════════════════════════════════════════════════════════════
SECTION 3: VERIFICATION [Grounding — Forces Evidence]
═══════════════════════════════════════════════════════════════════

For each item, verify:
□ Can I access this path? (If no, say "CANNOT ACCESS")
□ Did I run the check? (If no, say "NOT VERIFIED")
□ Is the data exact? (No approximations)

═══════════════════════════════════════════════════════════════════
SECTION 4: CONTEXT [Recency Zone — Can Be Truncated]
═══════════════════════════════════════════════════════════════════

[Reference material — optional, low priority]
```

---

## 6. SUMMARY: THE EXTRACTION COMMANDMENTS

| # | Commandment | Example |
|---|-------------|---------|
| 1 | **Thou shalt specify format first** | Table > paragraph |
| 2 | **Thou shalt embed verification** | "Run `git log` and report" |
| 3 | **Thou shalt forbid philosophy** | "No introductory text" |
| 4 | **Thou shalt require exactness** | "Copy path exactly" |
| 5 | **Thou shalt classify theater** | "Mark as STUB if..." |
| 6 | **Thou shalt constrain length** | "10 sentences max" |
| 7 | **Thou shalt punish hedging** | "YES/NO, not 'maybe'" |
| 8 | **Thou shalt cite evidence** | "Evidence: [file]" |
| 9 | **Thou shalt prioritize task** | Task in first 256 tokens |
| 10 | **Thou shalt verify status** | "Run the test, report result" |

---

## APPENDIX: BEFORE/AFTER EXAMPLES

### BEFORE (SECTION 1-6 style):
```markdown
## SECTION 1: Context
This project uses a dharmic approach to software...

## SECTION 2: Philosophy
The 17 gates represent...

## SECTION 3: Architecture
The system has multiple layers...

## SECTION 4: Task
Please analyze what files exist.
```
**Result:** Philosophy and preamble, no file listing.

### AFTER (Extraction-optimized):
```markdown
## TASK [First 256 tokens]
List all files in ~/clawd/handoffs/ with exact paths.

## FORMAT
| Filename | Size (bytes) | Modified |
|----------|--------------|----------|

## VERIFICATION
Run: `ls -la ~/clawd/handoffs/`
Copy output exactly. No paraphrasing.
```
**Result:** Exact file listing with sizes and timestamps.

---

*Research completed: 2026-02-17*  
*Sources: 5 subagent reports, codebase analysis, prompt engineering literature*  
*Key insight: Structure beats abstraction. Constraints enable precision.*
