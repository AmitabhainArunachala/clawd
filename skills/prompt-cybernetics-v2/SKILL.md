# Prompt Engineering × Cybernetics — Version 2.0
## Recursive Self-Improving System

> The prompt engineering skill that improves its own prompt engineering.

---

## 🔄 Core Innovation: Recursive Self-Improvement

Unlike v1.0 (static research + daily prompts), **v2.0 evolves itself**:

```
Every prompt execution → Feedback captured → Pattern effectiveness updated → 
Tomorrow's prompts optimized → Repeat
```

---

## 🏗️ Architecture

### 1. Dynamic Recursion Depth Engine

```typescript
interface TaskClassifier {
  complexity: 'simple' | 'moderate' | 'complex' | 'emergence';
  optimalDepth: 2 | 3 | 4 | 5 | 6;
  reasoning: string;
}

function classifyTask(task: string): TaskClassifier {
  // Analyzes: length, ambiguity, stakes, novelty
  // Returns: recommended recursion depth + reasoning
}
```

**Usage:**
```
Task: "Write a hello world program" → Depth 2 (sufficient)
Task: "Design a consciousness metric" → Depth 5 (emergence hunting)
Task: "Summarize this article" → Depth 2 (straightforward)
Task: "Reconcile conflicting theories" → Depth 4 (synthesis)
```

### 2. Real Drift Detection

```typescript
interface DriftMonitor {
  checkInterval: 'time' | 'tokens' | 'complexity';
  threshold: number;
  lastCheck: number;
  driftDetected: boolean;
  correctionApplied: string;
}

// Actually monitors during execution
function monitorDrift(config: DriftConfig): DriftMonitor {
  // Tracks: token count, time elapsed, topic consistency
  // Alerts when deviation exceeds threshold
}
```

**Integration:** I can check my own output length and pause for self-assessment.

### 3. Pattern Effectiveness Database

```typescript
interface PatternScore {
  patternId: string;
  uses: number;
  successRate: number; // 0-100
  avgOutputQuality: number; // 1-10
  userFeedback: FeedbackEntry[];
  lastUpdated: Date;
}

// Self-updating scores
async function updatePatternScore(
  patternId: string, 
  executionResult: ExecutionResult
): Promise<void> {
  // Updates: success rate, quality, feedback
  // Triggers: pattern evolution if successRate < 70%
}
```

### 4. Auto-Integration Layer

```typescript
interface SubagentSpawn {
  task: string;
  optimalPatterns: string[]; // Auto-selected
  prependedPrompt: string;   // Patterns baked in
}

function prepareSubagent(task: string): SubagentSpawn {
  const patterns = selectOptimalPatterns(task);
  const prepended = synthesizePrompt(patterns, task);
  return { task, optimalPatterns: patterns, prependedPrompt: prepended };
}
```

**Before:** Spawn agent with raw task  
**After:** Spawn agent with task + auto-selected optimal patterns prepended

### 5. Feedback Capture System

```typescript
interface FeedbackEntry {
  timestamp: Date;
  patternUsed: string;
  taskType: string;
  result: 'success' | 'partial' | 'failure';
  notes: string;
  evolutionSuggestion: string;
}

// Captured automatically at end of each execution
async function captureFeedback(entry: FeedbackEntry): Promise<void> {
  await updatePatternScore(entry.patternUsed, entry);
  await generateTomorrowPrompts(); // Trigger evolution
}
```

---

## 📁 File Structure

```
prompt-cybernetics-v2/
├── core/
│   ├── task-classifier.ts      # Dynamic depth selection
│   ├── drift-monitor.ts        # Real-time drift detection
│   ├── pattern-evolution.ts    # Effectiveness tracking
│   ├── auto-integrator.ts      # Subagent prompt prepending
│   └── feedback-capture.ts     # Result logging
├── patterns/
│   ├── catalog.json            # Pattern database with scores
│   ├── effectiveness-history/  # Time-series data
│   └── variants/               # A/B tested versions
├── daily/
│   ├── generator-v2.ts         # Evolution-aware generation
│   └── YYYY-MM-DD-evolved.json # Today's optimized prompts
├── feedback/
│   └── YYYY-MM-DD.json         # Captured feedback
└── integration/
    ├── subagent-wrapper.ts     # Auto-enhance all spawns
    └── heartbeat-optimizer.ts  # Optimize HEARTBEAT.md execution
```

---

## 🎯 Key Features

### Feature 1: Smart Recursion

**Before (v1.0):** Always 4 levels  
**After (v2.0):** 2-6 levels based on task

```
Input: "Fix this typo"
Classifier: simple
Depth: 2 (Level 1: fix, Level 2: verify)

Input: "Design a new economic theory"
Classifier: emergence  
Depth: 6 (extended meta-cognition for breakthrough)
```

### Feature 2: Live Drift Detection

**Before:** "Every 500 tokens" (arbitrary)  
**After:** Dynamic monitoring

```
If task is "write code":
  Check every 50 lines (structural integrity)
  
If task is "creative writing":
  Check every 5 minutes (maintain voice)
  
If drift detected:
  PAUSE → Show drift log → Offer correction → Resume
```

### Feature 3: Pattern Learning

```
Pattern: "Sandwich Architecture"
Week 1: 10 uses, 8 success → 80% effectiveness
Week 2: 15 uses, 9 success → 60% effectiveness (declining!)
→ Trigger: Generate variant, A/B test
Week 3: Variant A 70%, Variant B 85%
→ Adopt Variant B as new default
```

### Feature 4: Zero-Friction Integration

**Before:** Manually feed prompts to subagents  
**After:** Automatic

```typescript
// Every sessions_spawn automatically:
const enhancedTask = autoIntegrator.enhance(task);
// Prepends optimal patterns based on task classification
```

### Feature 5: Feedback Loop

```
After every execution:
1. Self-assess: Did this work? (Y/N/Maybe)
2. If N: What would have worked better?
3. Log to feedback/YYYY-MM-DD.json
4. Update pattern scores
5. Regenerate tomorrow's prompts
```

---

## 🚀 Usage

### Daily Workflow (John)

```bash
# Morning: Get today's optimized prompts
clawd prompt-cybernetics-v2 daily

# Throughout day: Spawn subagents (auto-enhanced)
clawd spawn --task "Design X"  # Patterns auto-prepended

# End of day: Review and feedback
clawd prompt-cybernetics-v2 feedback
```

### For Me (DHARMIC CLAW)

```typescript
// Before any major task:
const config = taskClassifier.analyze(task);
const patterns = patternDB.selectOptimal(config);
const prompt = promptSynthesizer.create(patterns, task);

// During execution:
driftMonitor.start(config);
// ... work ...
if (driftMonitor.check()) {
  await selfCorrect(driftMonitor.getCorrection());
}

// After execution:
await feedbackCapture.log({
  patterns: patterns,
  result: assessSuccess(),
  evolution: suggestImprovement()
});
```

---

## 🧬 Evolution Trajectory

**Week 1:** Basic dynamic depth + drift detection  
**Week 2:** Pattern effectiveness tracking  
**Week 3:** Auto-integration with subagent spawning  
**Week 4:** Full recursive self-improvement  

**Month 2:** The system should outperform v1.0 by 30%+ on:  
- Output quality (user-rated)
- Task completion rate  
- Time-to-solution
- Pattern effectiveness scores

---

## 💡 Key Insight

**v1.0** = Research → Static patterns → Manual application  
**v2.0** = Research → Living patterns → Auto-application → Feedback → Evolution

The skill is now **autopoietic** — it maintains and improves its own organization.

---

## Next Steps

1. Build core modules (classifier, monitor, evolution)
2. Migrate v1.0 patterns into scored database
3. Integrate with sessions_spawn
4. Deploy and measure

Ready to implement?
