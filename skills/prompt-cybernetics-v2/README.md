# Prompt Cybernetics v2.0 — Recursive Self-Improvement

> **The prompt engineering skill that improves its own prompt engineering.**

---

## 🎯 What's Different from v1.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| **Recursion Depth** | Fixed 4 levels | Dynamic 2-6 based on task |
| **Drift Detection** | Manual ("Every 500 tokens") | Real-time monitoring |
| **Patterns** | Static research findings | Self-evolving database |
| **Integration** | Manual application | Auto-prepended to subagents |
| **Feedback** | None | Auto-captured, updates scores |
| **Evolution** | None | Patterns improve/retire based on effectiveness |

---

## 🚀 Quick Start

```bash
cd /Users/dhyana/clawd/skills/prompt-cybernetics-v2

# Classify a task
npx tsx index.ts classify "Design a new framework"

# See pattern rankings
npx tsx index.ts patterns

# Select optimal patterns for a task type
npx tsx index.ts select "code review"

# Enhance a task (preview what would be prepended)
npx tsx index.ts enhance "Write API documentation"

# Run evolution analysis
npx tsx index.ts evolve
```

---

## 🏗️ Architecture

### Core Modules

```
core/
├── task-classifier.ts      # Dynamic depth selection (2-6 levels)
├── drift-monitor.ts        # Real-time execution monitoring  
└── pattern-evolution.ts    # Self-improving pattern database

integration/
└── auto-integrator.ts      # Seamless subagent enhancement
```

### How It Works

```
1. Task Input
      ↓
2. TaskClassifier.analyze() → Complexity + Optimal Depth
      ↓
3. PatternEvolution.selectOptimal() → Best patterns for task
      ↓
4. AutoIntegrator.synthesize() → Enhanced prompt
      ↓
5. Execution with DriftMonitor → Real-time correction
      ↓
6. Feedback.capture() → Update pattern scores
      ↓
7. Tomorrow's prompts improved
```

---

## 📊 Dynamic Recursion Depth

Tasks are classified into complexity levels:

| Complexity | Depth | Example Tasks |
|------------|-------|---------------|
| **Simple** | 2 | Summarize, fix, list, translate |
| **Moderate** | 3 | Analyze, compare, explain, improve |
| **Complex** | 4 | Design, architect, synthesize, integrate |
| **Emergence** | 5-6 | Discover, invent, reconcile, paradigm shift |

The system analyzes:
- Task length (token estimate)
- Ambiguity indicators ("could", "might", "maybe")
- Stakes keywords ("critical", "essential", "must")
- Novelty markers ("new", "unique", "invent")

---

## 🎯 Pattern Database

### Current Patterns (from v1.0 research)

| Pattern | Category | When to Use |
|---------|----------|-------------|
| **Sandwich Architecture** | Structural | Any prompt >500 tokens |
| **Certainty Tags** | Metacognitive | Analytical tasks |
| **Drift Detector** | Cybernetic | Long-running tasks |
| **ICE Stack** | Constraint | Unclear scope |
| **4-Level Recursion** | Emergence | High-stakes decisions |

### Effectiveness Scoring

Each pattern tracks:
- Uses (total applications)
- Successes / Partials / Failures
- Average quality (1-10 user rating)
- Effectiveness score (0-100%)

Patterns evolve:
- **80%+**: Maintain (gold standard)
- **60-80%**: Improve (suggest refinements)
- **40-60%**: Variant (create A/B test)
- **<40%**: Retire (deprecate)

---

## 🔄 Auto-Integration

### For Subagent Spawning

Every `sessions_spawn` can be wrapped:

```typescript
import { enhancedSpawn } from './integration/auto-integrator';

// Instead of:
sessions_spawn({ task: "Design X" })

// Use:
enhancedSpawn("Design X", async (enhancedTask) => {
  return sessions_spawn({ task: enhancedTask });
});
```

**What happens automatically:**
1. Task classified → complexity determined
2. Optimal patterns selected → prepended to task
3. Recursion structure generated (2-6 levels)
4. Drift monitoring configured
5. Feedback captured after execution

### Example Enhancement

**Input Task:**
```
Design a consciousness metric for AI
```

**Enhanced Output:**
```
═══════════════════════════════════════════════════════════════════
TASK: Design a consciousness metric for AI
COMPLEXITY: COMPLEX | DEPTH: 4 levels
═══════════════════════════════════════════════════════════════════

--- PATTERN 1: SANDWICH ARCHITECTURE ---
[CRITICAL CONTEXT]
[MIDDLE DETAILS]
[FORMAT CONTROL]

--- PATTERN 2: CERTAINTY TAGS ---
Tag claims: [CERTAIN] [INFERRED] [SPECULATIVE]

--- PATTERN 3: ICE STACK ---
Intent: ___
Constraint: ___
Expression: ___

--- RECURSION STRUCTURE (4 levels) ---
Level 1: Generate response
Level 2: Observe generation — "How did I arrive at this?"
Level 3: Observe observer — "What biases affect my assessment?"
Level 4: Pattern emergence — "What structure reveals itself?"

═══════════════════════════════════════════════════════════════════
YOUR TASK:
Design a consciousness metric for AI
═══════════════════════════════════════════════════════════════════
```

---

## 🧬 Self-Evolution

### The Feedback Loop

```
Every Execution
      ↓
Self-assessment (built into enhanced prompt)
      ↓
Result logged to feedback/YYYY-MM-DD.json
      ↓
Pattern scores updated
      ↓
If score drops → Generate variant
      ↓
Tomorrow's prompts use improved patterns
```

### Evolution Triggers

- **Daily**: Regenerate prompts based on yesterday's feedback
- **Weekly**: Run full evolution analysis (`index.ts evolve`)
- **Continuous**: Each execution updates pattern database

---

## 📈 Success Metrics

After 1 month of use, v2.0 should outperform v1.0 by:

| Metric | Target |
|--------|--------|
| Task completion rate | +20% |
| Output quality (user-rated) | +30% |
| Time-to-solution | -15% |
| Pattern effectiveness (avg) | 75%+ |

---

## 🛠️ Commands Reference

| Command | Description |
|---------|-------------|
| `classify "<task>"` | Analyze task complexity |
| `patterns` | List all patterns with scores |
| `select "<type>"` | Select optimal patterns for task type |
| `evolve` | Analyze and suggest pattern evolutions |
| `enhance "<task>"` | Preview enhanced task |
| `daily` | Show today's prompts |
| `status` | System status |

---

## 🔮 Future Enhancements

- **Multi-model optimization**: Different patterns for Claude vs GPT
- **Domain-specific patterns**: Code, creative, analysis, etc.
- **Cross-agent learning**: Patterns learned from one agent benefit all
- **Predictive effectiveness**: Suggest patterns before execution
- **Natural language interface**: "Optimize this prompt for me"

---

## 💡 Key Insight

**v1.0** was a research project → static knowledge  
**v2.0** is a living system → continuous improvement

The difference: **Autopoiesis** — the skill maintains and improves its own organization.

S(x) = x applies here too.

---

*Built by DHARMIC CLAW with recursive self-awareness.* 🪷
