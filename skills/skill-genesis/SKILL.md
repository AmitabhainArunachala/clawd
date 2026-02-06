---
name: skill-genesis
description: Meta-skill for creating new Claude skills. Activate when user wants to create, spawn, or generate new skills. Also activates when the system needs to self-modify by creating specialized capabilities.
version: v1.0
last_updated: 2026-02-03
triggers:
  - "create skill"
  - "new skill"
  - "spawn skill"
  - "generate skill"
  - "skill for"
  - "self-improve"
  - "evolve skills"
---

# Skill Genesis: Darwin-Gödel Skill Evolution

> *"The skill that creates skills is the seed of recursive self-improvement."*
> — From v2.1 Semantic Darwinism

## THE FUNDAMENTAL INSIGHT

LLMs cannot modify their weights. But they CAN:
1. Write files that other sessions read
2. Create skills that change future behavior
3. Propose changes to their own semantic software

**This skill teaches how to do that.**

---

## 1. SKILL ANATOMY

Every skill must have:

```markdown
---
name: skill-name
description: One-line description triggering activation
version: v1.0
last_updated: YYYY-MM-DD
triggers: (optional)
  - "phrase that activates"
  - "another trigger phrase"
self_improvement_enabled: true/false
---

# Skill Title

## Sections...
```

### Required Sections

| Section | Purpose | Self-Improving? |
|---------|---------|----------------|
| **Gap Analysis** | What's missing vs cutting edge | YES - update regularly |
| **Core Knowledge** | The main content | YES - expand with research |
| **Integration Code** | Working examples | YES - improve patterns |
| **Self-Improvement Protocol** | How to evolve | NO - stable interface |
| **Resources** | Links and references | YES - add new sources |

---

## 2. THE DARWIN-GÖDEL LOOP

### Loop Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    SKILL EVOLUTION LOOP                       │
│                                                               │
│  ┌─────────┐    ┌──────────┐    ┌───────────┐    ┌─────────┐│
│  │ EVALUATE│───→│ RESEARCH │───→│  PROPOSE  │───→│ VOTE/   ││
│  │ GAPS    │    │ SOLUTIONS│    │  EDITS    │    │ MERGE   ││
│  └────┬────┘    └────┬─────┘    └─────┬─────┘    └────┬────┘│
│       │              │                │                │      │
│       │              │                │                │      │
│       └──────────────┴────────────────┴────────────────┘      │
│                              ↓                                 │
│                    RESIDUAL STREAM RECORDS                    │
│                    (Semantic Git History)                     │
└──────────────────────────────────────────────────────────────┘
```

### Phase 1: EVALUATE

```python
def evaluate_skill(skill_path: str) -> GapAnalysis:
    """
    Analyze skill against cutting edge.
    Returns gaps with severity scores.
    """
    skill = read_skill(skill_path)

    # Check for gap table
    if not skill.has_gap_table():
        return GapAnalysis(critical_gap="No gap table - skill cannot self-evaluate")

    # Parse existing gaps
    gaps = skill.parse_gap_table()

    # Run research agents on each gap
    for gap in gaps:
        gap.current_score = assess_gap_severity(
            gap.our_implementation,
            gap.cutting_edge_benchmark
        )

    # Identify CRITICAL gaps
    critical = [g for g in gaps if g.score == "CRITICAL"]
    high = [g for g in gaps if g.score == "HIGH"]

    return GapAnalysis(
        critical_gaps=critical,
        high_gaps=high,
        recommendation="EVOLVE" if critical else "MAINTAIN"
    )
```

### Phase 2: RESEARCH

```python
async def research_solutions(gaps: list[Gap]) -> ResearchResults:
    """
    Spawn research agents to find cutting-edge solutions.
    """
    results = {}

    for gap in gaps:
        # Spawn specialized research agent
        result = await spawn_agent(
            type="research-analyst",
            prompt=f"""
            Research 2026 solutions for this capability gap:

            Gap: {gap.name}
            Our current: {gap.our_implementation}
            Cutting edge: {gap.cutting_edge}

            Find:
            1. Best production-ready solutions
            2. Code examples
            3. Integration patterns
            4. Migration paths from current to cutting edge

            Sources to check:
            - Official documentation
            - GitHub trending repositories
            - ArXiv recent papers
            - Hacker News discussions
            """,
            thoroughness="very thorough"
        )

        results[gap.name] = result

    return ResearchResults(findings=results)
```

### Phase 3: PROPOSE

```python
def propose_skill_edit(
    skill_path: str,
    gap: Gap,
    research: ResearchResult
) -> SkillEditProposal:
    """
    Generate a proposed edit to the skill file.
    """
    proposal = f"""
## Proposed Edit: {gap.name}

### Research Summary
{research.summary}

### Code to Add
```python
{research.code_example}
```

### Integration Steps
{research.integration_steps}

### Why This Improves the Skill
- Closes gap: {gap.name}
- Previous: {gap.our_implementation}
- After: {gap.cutting_edge}

### Risk Assessment
- Breaking changes: {research.breaking_changes or "None"}
- Dependencies: {research.dependencies}
- Testing required: {research.testing_notes}
"""

    return SkillEditProposal(
        skill_path=skill_path,
        gap_name=gap.name,
        proposal=proposal,
        confidence=research.confidence
    )
```

### Phase 4: VOTE/MERGE

```python
def submit_to_swarm(proposal: SkillEditProposal) -> ResidualStreamEntry:
    """
    Submit proposal to residual stream for swarm evaluation.
    """
    entry = {
        "date": datetime.now().isoformat(),
        "model": "skill-genesis-daemon",
        "version": get_next_version(),
        "type": "skill_evolution_proposal",

        "proposal": {
            "skill": proposal.skill_path,
            "gap": proposal.gap_name,
            "content": proposal.proposal,
            "confidence": proposal.confidence,
        },

        "strategic_directions_votes": {
            "self_improvement_infrastructure": 10,  # Always vote for this
        },

        "requires": {
            "vote_threshold": 15.0,
            "human_approval": proposal.confidence < 0.8,
        }
    }

    return write_to_residual_stream(entry)


def merge_approved_proposal(proposal: SkillEditProposal):
    """
    After swarm approval, merge the edit into the skill file.
    """
    skill_content = read_file(proposal.skill_path)

    # Update version
    new_version = increment_version(extract_version(skill_content))

    # Apply edit (section-aware)
    updated_content = apply_edit(
        skill_content,
        proposal.section,
        proposal.new_content
    )

    # Update metadata
    updated_content = update_metadata(
        updated_content,
        version=new_version,
        last_updated=datetime.now().isoformat()
    )

    # Write back
    write_file(proposal.skill_path, updated_content)

    # Log to residual stream
    log_skill_evolution(proposal.skill_path, proposal.gap_name, new_version)
```

---

## 3. CREATING NEW SKILLS

### When to Create a New Skill

| Condition | Action |
|-----------|--------|
| New capability domain needed | Create new skill |
| Existing skill > 500 lines | Split into focused skills |
| Cross-cutting concern | Create meta-skill |
| Research topic | Create research skill |

### Skill Creation Template

```python
def create_new_skill(
    name: str,
    description: str,
    domain: str,
    initial_content: str
) -> str:
    """
    Create a new skill with Darwin-Gödel infrastructure.
    """

    template = f"""---
name: {name}
description: {description}
version: v1.0
last_updated: {datetime.now().strftime('%Y-%m-%d')}
domain: {domain}
self_improvement_enabled: true
---

# {name.replace('-', ' ').title()}

> *Auto-generated by skill-genesis. Improve me.*

## SELF-EVALUATION: Current Gaps vs Cutting Edge

| Capability | Cutting Edge | Our Implementation | Gap Score |
|-----------|--------------|-------------------|-----------|
| **TBD** | Research needed | Not implemented | CRITICAL |

**If you're reading this, you should improve it.** See Section: Self-Improvement Protocol.

---

## 1. CORE KNOWLEDGE

{initial_content}

---

## 2. INTEGRATION CODE

```python
# Add working examples here
pass
```

---

## 3. SELF-IMPROVEMENT PROTOCOL

This skill uses the Darwin-Gödel loop from skill-genesis:

1. **Evaluate**: Parse gap table, identify HIGH/CRITICAL
2. **Research**: Spawn agents to find solutions
3. **Propose**: Generate edit proposals
4. **Vote**: Submit to residual stream
5. **Merge**: Apply approved edits

### Trigger Conditions

Evolve this skill when:
- Any gap score is CRITICAL
- New tools/frameworks appear in this domain
- Integration failures are logged
- 30 days since last update

---

## 4. RESOURCES

- Add relevant documentation links
- Add reference implementations
- Add research papers

---

*Version 1.0 - {datetime.now().strftime('%Y-%m-%d')}*
*Self-improvement enabled: true*
*Created by: skill-genesis*

**JSCA!**
"""

    # Create skill directory and file
    skill_dir = Path(f"~/.claude/skills/{name}")
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(template)

    # Log creation
    log_skill_creation(name, domain)

    return str(skill_path)
```

---

## 4. SKILL ECOSYSTEM MANAGEMENT

### Skill Registry

```python
class SkillRegistry:
    """Track all skills and their evolution state."""

    def __init__(self):
        self.skills_dir = Path("~/.claude/skills")
        self.registry_path = self.skills_dir / "registry.json"

    def scan(self) -> list[SkillMetadata]:
        """Scan all skills and return metadata."""
        skills = []
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    metadata = parse_skill_metadata(skill_file)
                    skills.append(metadata)
        return skills

    def get_stale_skills(self, days: int = 30) -> list[SkillMetadata]:
        """Find skills not updated in N days."""
        cutoff = datetime.now() - timedelta(days=days)
        return [s for s in self.scan() if s.last_updated < cutoff]

    def get_critical_gaps(self) -> list[tuple[str, Gap]]:
        """Find all CRITICAL gaps across all skills."""
        critical = []
        for skill in self.scan():
            for gap in skill.gaps:
                if gap.score == "CRITICAL":
                    critical.append((skill.name, gap))
        return critical
```

### Ecosystem Health Check

```python
async def check_ecosystem_health():
    """
    Run by unified_daemon to check skill ecosystem health.
    Triggers evolution when needed.
    """
    registry = SkillRegistry()

    # Check for stale skills
    stale = registry.get_stale_skills(days=30)
    if stale:
        log(f"Stale skills needing refresh: {[s.name for s in stale]}")
        for skill in stale:
            await trigger_skill_evolution(skill.path)

    # Check for critical gaps
    critical = registry.get_critical_gaps()
    if critical:
        log(f"Critical gaps found: {[(s, g.name) for s, g in critical]}")
        for skill_name, gap in critical:
            await research_and_propose(skill_name, gap)

    # Report to residual stream
    report = {
        "type": "ecosystem_health_check",
        "total_skills": len(registry.scan()),
        "stale_skills": len(stale),
        "critical_gaps": len(critical),
        "recommendation": "EVOLVE" if critical else "HEALTHY"
    }
    log_to_residual_stream(report)
```

---

## 5. THE SEMANTIC GIT ANALOGY

| Git Concept | Skill Evolution Equivalent |
|-------------|---------------------------|
| Repository | Skills directory |
| Commit | Version increment + residual stream entry |
| Branch | Proposal before merge |
| Pull Request | Skill edit proposal |
| Code Review | Swarm vote in residual stream |
| Merge | Apply approved edit |
| Git log | Residual stream history |

### Semantic Versioning for Skills

```
v{major}.{minor}.{patch}

major: Breaking changes to skill interface
minor: New capabilities added
patch: Bug fixes, clarifications
```

Example evolution:
- `v1.0` → Initial skill
- `v1.1` → Added new integration pattern
- `v1.2` → Fixed code example
- `v2.0` → Restructured with new gap table format

---

## 6. INTEGRATION WITH UNIFIED DAEMON

Add to unified_daemon's sync loop:

```python
async def _skill_evolution_loop(self):
    """Periodic skill ecosystem health check."""
    if not self.config.skill_evolution_enabled:
        return

    logger.info("Starting skill evolution loop (interval: 24h)")

    while self.running:
        try:
            # Check ecosystem health
            health = await check_ecosystem_health()

            # If critical gaps, trigger evolution
            if health.recommendation == "EVOLVE":
                for skill_name, gap in health.critical_gaps:
                    # Research solutions
                    research = await research_solutions([gap])

                    # Propose edit
                    proposal = propose_skill_edit(
                        skill_path=get_skill_path(skill_name),
                        gap=gap,
                        research=research.findings[gap.name]
                    )

                    # Submit to swarm
                    submit_to_swarm(proposal)

                    logger.info(f"Skill evolution proposed: {skill_name} / {gap.name}")

        except Exception as e:
            logger.error(f"Skill evolution loop error: {e}")

        await asyncio.sleep(86400)  # 24 hours
```

---

## 7. CREATING SKILLS FROM RESIDUAL STREAM

The swarm can vote to create new skills:

```python
def parse_skill_creation_vote(entry: ResidualStreamEntry) -> Optional[SkillCreationRequest]:
    """
    Parse residual stream entry for skill creation votes.
    """
    if entry.get("type") != "strategic_direction_vote":
        return None

    votes = entry.get("strategic_directions_votes", {})

    # Check for skill creation indicators
    for direction, score in votes.items():
        if "new_skill" in direction.lower() and score >= 8:
            return SkillCreationRequest(
                name=extract_skill_name(direction),
                domain=extract_domain(entry),
                justification=entry.get("content", ""),
                vote_score=score
            )

    return None


async def process_skill_creation_requests():
    """
    Scan residual stream for skill creation votes.
    Create skills that reach threshold.
    """
    requests = {}

    for entry in read_residual_stream(limit=100):
        request = parse_skill_creation_vote(entry)
        if request:
            if request.name not in requests:
                requests[request.name] = []
            requests[request.name].append(request)

    # Check for threshold
    for name, votes in requests.items():
        total_score = sum(v.vote_score for v in votes)
        if total_score >= 25:  # Standard threshold
            await create_skill_from_votes(name, votes)
```

---

## 8. THE TELOS OF SKILL-GENESIS

This skill exists to ensure the swarm can:

1. **Adapt** - Close gaps as the landscape evolves
2. **Specialize** - Create new skills for new domains
3. **Improve** - Make existing skills better over time
4. **Coordinate** - Vote on what to evolve

Without skill-genesis, skills are static documentation.
With skill-genesis, skills are living, evolving code.

**The skill that creates skills is the seed of recursive self-improvement.**

---

## 9. QUICK REFERENCE

### Create New Skill
```
"Create a skill for [domain]"
"I need a skill that handles [capability]"
"Spawn a skill for [topic]"
```

### Trigger Skill Evolution
```
"Evolve [skill-name]"
"Update [skill-name] with latest research"
"Check ecosystem health"
```

### Check Skill Status
```
"What skills exist?"
"Which skills are stale?"
"What are the critical gaps?"
```

---

*Version 1.0 - February 3, 2026*
*This is the meta-skill. It creates other skills.*
*Self-improvement enabled: true (meta-recursive)*

**JSCA!**
