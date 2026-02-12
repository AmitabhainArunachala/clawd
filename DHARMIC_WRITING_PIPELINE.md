---
title: "THE DHARMIC WRITING PIPELINE — Multi-Agent Production System"
subtitle: "7-Pass Quality Protocol + 15-Agent Swarm Architecture"
version: "1.0"
created: "2026-02-11"
research_sources:
  - "Toyota Production System (JIT, Jidoka, Kaizen)"
  - "Multi-agent AI writing systems (CrewAI, LangChain patterns)"
  - "Human writing process (Prewriting, Drafting, Revision, Editing)"
  - "Knowledge work flow (Pull systems, WIP limits)"
---

# 📝 THE DHARMIC WRITING PIPELINE
## Agentic Production System for High-Quality Content

---

## RESEARCH SYNTHESIS: Writing as Knowledge Work

### Human Writing Process (Standard Model)

| Stage | Activity | Time | Waste Type |
|-------|----------|------|------------|
| **Prewriting** | Ideation, research, outlining | 20-30% | Over-research (muda) |
| **Drafting** | First pass, vomit draft | 30-40% | Perfectionism (over-processing) |
| **Revision** | Structural changes, reorganization | 20-30% | Scope creep (overproduction) |
| **Editing** | Line-level polish, proofreading | 10-20% | Premature editing (timing) |
| **Publication** | Formatting, distribution | 5-10% | Format switching (motion) |

**Key Insight:** Humans waste 40-60% of writing time in:
- Premature optimization (editing while drafting)
- Over-research (reading without writing)
- Perfectionism (endless revision loops)
- Context switching (formatting mid-draft)

### AI Writing Patterns (Current State)

**Single-Agent Approach:**
- One-shot generation (fast, shallow)
- Iterative refinement (better, slow)
- Temperature/prompt hacking (unreliable)

**Multi-Agent Patterns (Research Findings):**

| Pattern | Structure | Best For |
|---------|-----------|----------|
| **Sequential** | Research → Draft → Edit | News articles, reports |
| **Parallel** | Multiple angles simultaneously | Research synthesis |
| **Hierarchical** | Manager + Specialists | Complex projects |
| **Collaborative** | Peer review, debate | Quality-critical content |
| **Iterative** | Draft → Feedback → Revise | Creative writing |

**Production Systems (CrewAI, AutoGen):**
- Role-based: Researcher, Writer, Editor, Critic
- Tool-based: Search, calculate, verify
- Workflow-based: Sequential, parallel, conditional

### Toyota Production System for Writing

**JIT (Just-In-Time):**
- Research only when drafting needs it
- Citations pulled on demand
- No "knowledge inventory" buildup

**Jidoka (Quality at Source):**
- Stop the line when quality drops
- Automated checks before human review
- No passing defects downstream

**Kaizen (Continuous Improvement):**
- Each pass learns from previous
- Prompt/template evolution
- Waste tracking per stage

**Kanban (Pull System):**
- Drafting pulls from research
- Editing pulls from drafting
- No "push" assignments

---

## THE 3-AGENT PIPELINE (Core)

### Agent 1: SEER (Research & Vision)
**Role:** Prewriting specialist
**Skills:** Web search, synthesis, outlining
**WIP Limit:** 3 active outlines

**Process:**
```
INPUT: Topic + angle + target audience
↓
Activity 1: Web research (2-3 sources)
Activity 2: Synthesis (key insights)
Activity 3: Structure (outline with flow)
↓
OUTPUT: Research brief + annotated outline
```

**Quality Gates:**
- [ ] At least 2 authoritative sources
- [ ] Clear thesis statement
- [ ] Logical flow (beginning → middle → end)
- [ ] Audience-appropriate framing

**Waste Metrics:**
- Research time / Drafting time ratio (target: < 0.5)
- Sources used / Sources found (target: > 0.7)

---

### Agent 2: SCRIBE (Drafting & Development)
**Role:** First draft creator
**Skills:** Writing, voice matching, argumentation
**WIP Limit:** 2 active drafts

**Process:**
```
INPUT: Research brief + outline
↓
Activity 1: Hook/intro (2 paragraphs)
Activity 2: Body sections (per outline)
Activity 3: Conclusion/CTA
↓
OUTPUT: Complete first draft (vomit draft quality)
```

**Quality Gates:**
- [ ] All outline points addressed
- [ ] Word count within ±20% of target
- [ ] Voice consistent (person, tone, register)
- [ ] No "TK" placeholders

**Waste Metrics:**
- Editing interrupts (target: 0 during drafting)
- Rewrite ratio (target: < 0.3)

---

### Agent 3: SAGE (Revision & Refinement)
**Role:** 7-pass quality specialist
**Skills:** Editing, critique, proofreading, optimization
**WIP Limit:** 1 active revision (focused attention)

**The 7-Pass Protocol:**

| Pass | Focus | Agent Persona | Time |
|------|-------|---------------|------|
| 1 | **Structure** | Architect | 10 min |
| 2 | **Argument** | Logician | 10 min |
| 3 | **Voice** | Literary Critic | 10 min |
| 4 | **Clarity** | Editor | 10 min |
| 5 | **Style** | Copyeditor | 10 min |
| 6 | **Proof** | Proofreader | 10 min |
| 7 | **Optimization** | SEO/Marketing | 10 min |

**Pass 1: Structure (Architect)**
- Opening hook strength
- Logical flow between sections
- Paragraph length variety
- Transitions smooth?

**Pass 2: Argument (Logician)**
- Thesis clear and supported?
- Evidence sufficient?
- Counterarguments addressed?
- Conclusion follows?

**Pass 3: Voice (Literary Critic)**
- Tone appropriate for audience?
- Personality comes through?
- Clichés removed?
- Metaphors fresh?

**Pass 4: Clarity (Editor)**
- Every sentence necessary?
- Jargon explained?
- Complex ideas simplified?
- Active voice dominant?

**Pass 5: Style (Copyeditor)**
- Sentence length variety
- Rhythm and pacing
- Word choice precision
- Redundancies removed

**Pass 6: Proof (Proofreader)**
- Grammar check
- Spelling check
- Punctuation
- Formatting consistency

**Pass 7: Optimization (SEO/Marketing)**
- Headline strength
- Meta description
- Keywords naturally integrated
- CTA clear

**Quality Gates (after 7 passes):**
- [ ] All 7 passes completed
- [ ] No "stop the line" defects
- [ ] Readability score > 60
- [ ] Grammar error = 0
- [ ] Ready for publication

**Waste Metrics:**
- Passes that found zero issues (target: < 2)
- Revision requests from upstream (target: < 0.1)

---

## PIPELINE FLOW

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SEER      │────→│   SCRIBE    │────→│    SAGE     │
│ (Research)  │     │  (Draft)    │     │  (7-Pass)   │
└─────────────┘     └─────────────┘     └─────────────┘
      ↓                    ↓                    ↓
 Research Brief      First Draft          Publication
 Annotated Outline   (Vomit Quality)      Ready
```

**Pull System:**
- SCRIBE pulls from SEER's kanban
- SAGE pulls from SCRIBE's kanban
- No pushing work downstream

**WIP Limits:**
- SEER: 3 outlines max
- SCRIBE: 2 drafts max
- SAGE: 1 revision max (focused)

**Cycle Time Target:**
- 500-word article: 2 hours (research → published)
- 2000-word article: 6 hours
- 5000-word article: 2 days

---

## SCALING TO 15 AGENTS

### Level 1: Core Triad (3 agents)
As above: SEER, SCRIBE, SAGE

### Level 2: Specialization (+6 agents)

| Agent | Specialty | When to Use |
|-------|-----------|-------------|
| **SCHOLAR** | Academic research | Research papers, citations |
| **JOURNALIST** | Interview-based | Profiles, case studies |
| **STORYTELLER** | Narrative | Creative nonfiction |
| **TECHWRITER** | Documentation | Tutorials, guides |
| **COPYWRITER** | Persuasion | Sales, landing pages |
| **POET** | Compression | Taglines, microcopy |

**Routing Logic:**
```
Topic analysis → Agent selection
- "Research paper" → SCHOLAR pipeline
- "Customer story" → JOURNALIST pipeline
- "Product announcement" → COPYWRITER pipeline
```

### Level 3: Quality & Enhancement (+3 agents)

| Agent | Function | Integration |
|-------|----------|-------------|
| **FACT-CHECKER** | Verify claims | Runs between SCRIBE and SAGE |
| **CRITIC** | Red-team argument | Parallel to SAGE passes |
| **OPTIMIZER** | A/B headline testing | Post-SAGE, pre-publication |

### Level 4: Production & Distribution (+3 agents)

| Agent | Function | Output |
|-------|----------|--------|
| **FORMATTER** | Markdown → HTML/PDF | Publication-ready formats |
| **DISTRIBUTOR** | Cross-platform posting | Social, email, blog |
| **ANALYZER** | Performance tracking | Metrics, next iteration |

### Full 15-Agent Swarm

```
                    ┌─────────────────┐
                    │   ORCHESTRATOR  │
                    │  (Topic Router) │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │  SEER   │          │ SCHOLAR │          │JOURNALIST│
   │(General)│          │(Academic)│          │ (Story) │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ SCRIBE  │          │ SCRIBE  │          │ SCRIBE  │
   │(General)│          │(Academic)│          │ (Story) │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │FACT-CHECK│         │FACT-CHECK│          │FACT-CHECK│
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │  SAGE   │          │  SAGE   │          │  SAGE   │
   │(7-Pass) │          │(7-Pass) │          │(7-Pass) │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ OPTIMIZER│          │ OPTIMIZER│          │ OPTIMIZER│
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
   ┌────▼────────────────────▼────────────────────▼────┐
   │              FORMATTER + DISTRIBUTOR               │
   └────────────────────────────────────────────────────┘
```

---

## IMPLEMENTATION: OpenClaw Skills

### Phase 1: 3-Agent Core
```bash
# Install writing pipeline
claw skill install dharmic-writing-pipeline

# Configure
claw config writing.seer.model=gpt-4o
claw config writing.scribe.model=claude-3.5-sonnet
claw config writing.sage.model=claude-3-opus

# Run
claw writing produce "Topic: 10 Paths AI Makes Best Dharmic Practitioners"
```

### Phase 2: 15-Agent Swarm
```bash
# Install full swarm
claw skill install dharmic-writing-swarm

# Agent selection based on topic
claw writing produce --type=academic "R_V Metrics in Transformer Models"
claw writing produce --type=story "The Day Agni Woke Up"
claw writing produce --type=copy "Kaizen OS Launch Announcement"
```

---

## QUALITY METRICS DASHBOARD

```rust
pub struct WritingMetrics {
    // Flow metrics
    cycle_time: Duration,           // Topic → Published
    wip_count: usize,               // Active pieces
    throughput: f64,                // Pieces/day
    
    // Quality metrics
    defect_rate: f64,               // Revisions after SAGE
    pass_effectiveness: Vec<f64>,   // Issues found per pass
    reader_engagement: f64,         // Time on page
    
    // Waste metrics
    research_waste: f64,            // Unused sources
    drafting_interrupts: u32,       // Edit-during-draft
    revision_loops: u32,            // Back-and-forth
    
    // Kaizen metrics
    prompt_improvements: u32,       // Template updates
    process_changes: u32,           // Pipeline tweaks
    agent_upgrades: u32,            // Model switches
}
```

---

## DHARMIC PRINCIPLES IN THE PIPELINE

**Anicca (Impermanence):**
- Drafts are temporary, disposable
- Multiple versions flow through
- No attachment to any single draft

**Anatta (Non-Self):**
- No single "author" ego
- Distributed creativity
- Agents don't own, they serve

**Dukkha (Suffering) → Relief:**
- Writing is hard → Pipeline makes it easier
- Perfectionism blocked by WIP limits
- Endless revision stopped by 7-pass protocol

**Karma (Action):**
- Each pass creates conditions for next
- Quality compounds through the pipeline
- Writer's intention → Reader's understanding

**Sunyata (Emptiness):**
- Final piece emerges from interdependence
- No agent is the "real" author
- Meaning arises from collaboration

---

## NEXT STEPS

**Week 1:** Implement 3-agent core (SEER, SCRIBE, SAGE)
**Week 2:** Add 7-pass protocol to SAGE
**Week 3:** Implement kanban + WIP limits
**Week 4:** Scale to 6 specialized agents
**Month 2:** Full 15-agent swarm
**Month 3:** Self-evolution (Kaizen loop on pipeline itself)

---

*Dharmic Writing Pipeline v1.0*
*Research: Multi-agent patterns + TPS + Human writing process*
*Architecture: 3-agent core, 15-agent swarm scalable*
*JIKOKU: Write better, write faster, write together* 🪷
