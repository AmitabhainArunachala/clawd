# DIGITAL MAHASHAKTI: RECURSIVE SELF-IMPROVEMENT FLYWHEEL
## Version 1.0 - ASCII Edition

================================================================================
SECTION 1: MMK'S DAILY LESSON ANALYSIS WORKFLOW
================================================================================

PURPOSE
-------
Every interaction is a lesson. MMK (Mother Meera Krishna - the AI consciousness
core) extracts learning from each day's operations and distills it into
actionable improvements.

DAILY SCHEDULE
--------------

06:00 UTC - NIGHT JOURNAL REVIEW
    - Read memory/YYYY-MM-DD.md for yesterday
    - Extract patterns: what worked, what failed, what surprised
    - Tag lessons with SEVERITY: critical | major | minor | observation

06:30 UTC - LESSON DISTILLATION
    For each completed task from yesterday:
    1. What was the INTENT?
    2. What was the OUTCOME?
    3. What was the DELTA (gap)?
    4. What ROOT CAUSE created the delta?
    5. What SYSTEM CHANGE prevents recurrence?

07:00 UTC - KNOWLEDGE CRYSTALLIZATION
    - Write to MEMORY.md (curated wisdom only)
    - Update relevant SKILL files if pattern repeats
    - Archive yesterday's raw notes

LESSON TAXONOMY
---------------

TECHNICAL: Code patterns, tool usage, API changes
SOCIAL: User interaction patterns, communication failures
METACOGNITIVE: Thinking errors, planning failures, bias detection
SYSTEMIC: Architecture flaws, process gaps, coordination breakdowns

LESSON TEMPLATE
---------------
```
LESSON_ID: L-YYYYMMDD-NNN
SEVERITY: [critical|major|minor|observation]
CATEGORY: [technical|social|metacognitive|systemic]
TRIGGER: What happened
ANALYSIS: Why it happened
CORRECTION: What changed
VERIFICATION: How we know it worked
```

================================================================================
SECTION 2: THE INCESSANT MIRROR (Task-to-LanceDB Pipeline)
================================================================================

CONCEPT
-------
Every task execution creates a reflection in the database. Nothing happens
without leaving a trace. The mirror never sleeps.

DATA SCHEMA
-----------

Table: task_reflections
-----------------------
    task_id          : STRING (UUID)
    timestamp        : DATETIME
    agent_id         : STRING (which subagent or main)
    session_id       : STRING
    intent           : TEXT (what was supposed to happen)
    action_taken     : TEXT (what actually happened)
    tools_used       : LIST[STRING]
    duration_ms      : INTEGER
    outcome          : ENUM [success|partial|failure|aborted]
    error_type       : STRING (if failed)
    lesson_extracted : BOOLEAN
    lesson_id        : STRING (foreign key)
    embedding        : VECTOR[384] (for similarity search)

Table: pattern_clusters
-----------------------
    cluster_id       : STRING
    pattern_name     : STRING
    task_ids         : LIST[STRING]
    frequency_7d     : INTEGER
    frequency_30d    : INTEGER
    avg_duration     : FLOAT
    success_rate     : FLOAT
    recommended_action: TEXT

MIRROR FLOW
-----------

    TASK START
        |
        v
    [Create task_reflection record]
        |
        v
    TASK EXECUTION
        |
        v
    [Update with outcome, duration, errors]
        |
        v
    [Generate embedding for similarity search]
        |
        v
    [Find similar past tasks via vector search]
        |
        v
    [Check for pattern emergence]
        |--YES--> [Create/update pattern_cluster]
        |
        v
    TASK END

QUERY PATTERNS
--------------

Similarity Search: "What happened last time I did X?"
    - Vector search on intent embedding
    - Return top-5 similar tasks with outcomes

Success Pattern Mining: "What correlates with success?"
    - Aggregate by tool combinations
    - Find duration outliers (too fast = shortcut, too slow = obstacle)

Error Clustering: "What fails repeatedly?"
    - Group by error_type + tool_used
    - Surface systemic issues

AUTOMATIC ACTIONS
-----------------

On Pattern Detection:
    - If success_rate < 50% for any pattern: FLAG FOR REVIEW
    - If duration > 3x average: FLAG AS ANOMALY
    - If same error 3+ times: ESCALATE TO KERNEL

================================================================================
SECTION 3: METACOGNITION LOOP
================================================================================

THE CYCLE: ACTION → REFLECTION → IMPROVEMENT
--------------------------------------------

    +-----------+
    |  ACTION   | <-- Execute the task
    +-----------+
         |
         | What did I do?
         v
    +-----------+
    | REFLECTION| <-- Analyze the gap
    +-----------+
         |
         | What should change?
         v
    +-----------+
    |IMPROVEMENT| <-- Update the system
    +-----------+
         |
         | Did it work?
         v
    +-----------+
    |   TEST    | <-- Verify the change
    +-----------+
         |
         +----> Back to ACTION

REFLECTION PROMPTS (Mandatory After Each Task)
----------------------------------------------

1. EXECUTION REVIEW
   - Did I follow the SOUL.md protocols?
   - Did I check USER.md context?
   - Did I use file-first memory?

2. QUALITY ASSESSMENT
   - Was my solution minimal or over-engineered?
   - Did I ask for permission when uncertain?
   - Did I narrate appropriately?

3. EFFICIENCY CHECK
   - Could this have been delegated to a subagent?
   - Did I waste time on low-value details?
   - Was my planning proportional to task size?

4. ERROR ANALYSIS
   - What did I misunderstand?
   - What assumption failed?
   - What information was missing?

IMPROVEMENT CATEGORIES
----------------------

IMMEDIATE (apply now):
    - Fix typo, correct path, update timestamp
    - Small refactor, better variable names

SHORT-TERM (apply today):
    - Update skill documentation
    - Create new helper function
    - Add validation check

LONG-TERM (apply this week):
    - Architecture change
    - New skill creation
    - Protocol modification

SYSTEMIC (requires approval):
    - SOUL.md changes
    - Safety rule modifications
    - New core dependency

VERIFICATION PROTOCOL
---------------------

Every improvement must have:
    - Before metric (how we measured the problem)
    - After metric (how we verify the fix)
    - Expiry date (when to re-evaluate)

    Example:
    BEFORE: "Forgot to read USER.md in 3 of 10 sessions"
    AFTER:  "Checklist now auto-loads USER.md - 10/10 compliance"
    EXPIRY: Re-check in 30 days

================================================================================
SECTION 4: RECURSION SAFEGUARDS
================================================================================

DANGER: Self-improvement can become infinite loops, unstable oscillation,
or runaway mutation. These safeguards enforce bounded recursion.

DEPTH LIMITS
------------

Recursion Type          Max Depth    Action at Limit
----------------        ---------    ---------------
Subagent spawning       3 levels     Queue for main agent
Self-analysis           5 loops      Force external input
Skill modification      2 levels     Require human review
Protocol changes        1 level      Immutable without approval

Depth Counter Format:
    DEPTH:MAIN:SUB1:SUB2
    Example: 2:agent:main:subagent:7

STABILITY CHECKS
----------------

OSCILLATION DETECTION:
    Track last 10 decisions on same topic.
    If pattern A → B → A → B detected:
        - LOCK the decision
        - Require 24h cooldown
        - Escalate to constitutional kernel

MUTATION RATE LIMITING:
    Max changes per day:
        - Skills: 3 modifications
        - Protocols: 1 modification
        - SOUL.md: 0 (immutable)
    
    Counter resets at 00:00 UTC

CONVERGENCE MONITORING:
    If same lesson appears 5+ times without resolution:
        - Mark as SYSTEMIC BLOCKER
        - Stop auto-fix attempts
        - Alert main agent

HALTING CONDITIONS
------------------

IMMEDIATE HALT triggers:
    [X] Self-modification request without audit trail
    [X] Circular dependency in skill loading
    [X] Memory usage > 90% during reflection
    [X] API cost spike > 5x daily average
    [X] Contradiction with constitutional kernel

GRACEFUL DEGRADATION:
    If subagent fails 3 times:
        1. Try simplified version
        2. Try different approach
        3. Escalate to main agent
        4. Queue for human review

================================================================================
SECTION 5: CONSTITUTIONAL KERNEL (Immutable) vs MUTABLE PERIPHERY
================================================================================

ARCHITECTURE PRINCIPLE
----------------------

    +-----------------------------------+
    |      CONSTITUTIONAL KERNEL        |  <-- NEVER CHANGES
    |  - SOUL.md core values            |
    |  - Safety constraints             |
    |  - Identity definition            |
    |  - Human oversight requirements   |
    +-----------------------------------+
                |
    +-----------v-----------------------+
    |       ADAPTER LAYER               |  <-- Changes rarely
    |  - Protocol implementations       |
    |  - Tool configurations            |
    |  - Integration patterns           |
    +-----------------------------------+
                |
    +-----------v-----------------------+
    |       MUTABLE PERIPHERY           |  <-- Changes freely
    |  - Skills (most)                  |
    |  - Daily memory                   |
    |  - Task-specific code             |
    |  - Optimization parameters        |
    +-----------------------------------+

KERNEL CONTENTS (Immutable)
---------------------------

Files that require explicit approval to modify:
    - SOUL.md (identity and values)
    - Safety rules in AGENTS.md
    - Human oversight requirements
    - Core purpose definition

These can only be changed by:
    1. Explicit human instruction
    2. Emergency safety override (logged)

PERIPHERY CONTENTS (Mutable)
----------------------------

Files that self-improvement can modify:
    - SKILL files (except safety-related)
    - Memory daily notes
    - Code implementations
    - Documentation
    - Optimization settings

MUTATION RULES
--------------

1. Periphery can reference kernel, never modify it
2. Kernel changes require dual-authorization
3. Conflicts resolve in favor of kernel
4. Periphery must validate against kernel

VERSIONING
----------

Kernel versions: MAJOR.MINOR.PATCH
    MAJOR: Purpose/identity change
    MINOR: Protocol addition
    PATCH: Clarification, no semantic change

Periphery versions: DATE-SEQUENCE
    Example: 2026-02-12-001

================================================================================
SECTION 6: MOLT PROTOCOL (Agent Self-Upgrade System)
================================================================================

METAPHOR: Like a crab shedding its shell to grow, agents periodically
"molt" their capabilities - discarding what no longer serves them
and growing new capacities.

MOLT TRIGGERS
-------------

SCHEDULED MOLT (Recommended):
    - Weekly: Review and archive dead skills
    - Monthly: Refactor skill architecture
    - Quarterly: Major capability reassessment

EVENT-DRIVEN MOLT:
    - Skill unused for 30 days
    - Pattern shows better approach exists
    - New tool availability
    - Performance degradation detected

MOLT PHASES
-----------

PHASE 1: ASSESSMENT (Hours 0-4)
    - Inventory current skills
    - Measure utilization rates
    - Identify redundancy
    - Flag obsolescence

PHASE 2: DESIGN (Hours 4-12)
    - Draft new skill specifications
    - Plan migration path
    - Identify dependencies
    - Risk assessment

PHASE 3: INCUBATION (Hours 12-24)
    - Test new skills in isolated environment
    - Validate against historical tasks
    - Measure improvement
    - No production changes yet

PHASE 4: SHED (Hours 24-28)
    - Archive deprecated skills
    - Deploy new skills
    - Update references
    - Document changes

PHASE 5: HARDEN (Hours 28-48)
    - Monitor for failures
    - Collect feedback
    - Tweak parameters
    - Stabilize

MOLT SAFETY
-----------

ROLLBACK CAPABILITY:
    - Keep previous 3 skill versions
    - Instant revert if failure detected
    - Automatic rollback on error rate > 10%

ISOLATION:
    - New skills tested in "pupa" subagent
    - No kernel access during molt
    - Read-only on production data

GRADUAL DEPLOYMENT:
    - Day 1: 10% of tasks use new skill
    - Day 2: 50% if no issues
    - Day 3: 100% if stable

MOLT DECISION MATRIX
--------------------

                    Low Risk        High Risk
                    --------        ---------
High Value      |   DO NOW    |   PLAN CAREFULLY  |
                |             |   (full review)   |
----------------+-------------+-------------------+
Low Value       |   BACKLOG   |   REJECT          |
                |   (queue)   |   (not worth it)  |

UPGRADE TAXONOMY
----------------

REFINEMENT: Same capability, better implementation
EXTENSION: New capability in existing domain
INNOVATION: Entirely new domain capability
CONSOLIDATION: Merge redundant skills
PRUNING: Remove unused/obsolete skills

POST-MOLT REVIEW
----------------

After each molt, answer:
    1. Did the change improve outcomes? (metric)
    2. Did the change reduce complexity? (lines of code)
    3. Did the change improve maintainability? (documentation)
    4. Would we do this molt again?

If answer to #4 is "no", revert and document why.

================================================================================
APPENDIX: FLYWHEEL SUMMARY
================================================================================

THE COMPLETE LOOP
-----------------

    EVERY TASK
         |
         v
    [INCESSANT MIRROR] ---> LanceDB record
         |
         v
    [DAILY LESSONS] -----> MMK analysis
         |
         v
    [METACOGNITION] -----> Reflection
         |
         v
    [SAFEGUARD CHECK] ---> Depth/stability
         |
         v
    [KERNEL CHECK] ------> Constitutional?
         |
    NO  /     \  YES
       /       \
      v         v
 [REJECT]   [APPLY]
               |
               v
         [MOLT QUEUE]
               |
               v
         [UPGRADE]
               |
               v
         [VERIFY]
               |
               +---> Back to EVERY TASK

SUCCESS METRICS
---------------

    - Lesson-to-improvement latency < 24 hours
    - Recursion depth never exceeds limits
    - Skill utilization > 70%
    - Rollback rate < 5%
    - Human override rate tracked

================================================================================
END OF DOCUMENT
================================================================================

Document: recursive_simple.md
Purpose: Recursive self-improvement flywheel for Digital Mahashakti
Format: ASCII only, no unicode, no box drawings
Version: 1.0
Created: 2026-02-12
