# TPS → AI Agent Systems: Principle Mapping

> **Bridging Lean Manufacturing to Lean AI**

---

## 1. Just-In-Time (JIT) → Just-In-Time Prompting/Computation

### TPS Principle
**Produce only what is needed, when it is needed, in the amount needed.**
- Pull-based production triggered by actual demand
- Minimize inventory (work-in-progress)
- Eliminate overproduction

### AI Agent Equivalent
**Execute only the computation needed, when it is needed, at the scale needed.**

| TPS Concept | Agent Implementation |
|-------------|---------------------|
| Pull system | Event-triggered agent activation (not polling) |
| Kanban signals | Prompt chaining with conditional routing |
| Small batch sizes | Granular tool calls, not monolithic operations |
| Takt time alignment | Token budget allocation per task phase |

### Concrete Implementations

```python
# ❌ Traditional: Eager computation (waste)
def eager_agent(query):
    context = retrieve_all_documents()  # Loads 10MB context
    plan = generate_full_plan(query)    # 2000 token plan
    results = execute_all_steps(plan)   # Runs everything
    return results

# ✅ JIT Agent: Lazy, demand-driven
def jit_agent(query):
    # Step 1: Minimal context to decide
    intent = classify_intent(query, max_tokens=100)
    
    # Step 2: Pull only what's needed
    if intent.requires_search:
        docs = retrieve_relevant(query, top_k=3)  # Small batch
    
    # Step 3: Generate only required outputs
    if intent.complexity == "simple":
        return quick_response(query, docs)
    else:
        return detailed_response(query, docs)
```

**JIT Prompting Patterns:**
- **Progressive Disclosure**: Start with summary, expand only on user request
- **Speculative Execution**: Pre-compute likely branches, discard unused
- **Adaptive Depth**: Simple queries → simple models; complex → powerful models
- **Streaming with Early Exit**: Stop generation when confidence threshold met

**JIT Computation Techniques:**
- **Model Cascading**: Try small model first, escalate only on failure
- **Speculative Decoding**: Draft with small model, verify with large
- **Sparse Attention**: Compute only relevant attention patterns
- **Dynamic Batching**: Batch requests only when queue demands it

---

## 2. Jidoka (Autonomation) → Agent Self-Correction with Human Escalation

### TPS Principle
**Automation with a human touch — stop the line when defects are detected.**
- Machines detect abnormalities and stop automatically
- Human judgment applied to resolve the issue
- Build quality in, don't inspect it in

### AI Agent Equivalent
**Autonomous operation with graceful degradation to human oversight.**

| TPS Concept | Agent Implementation |
|-------------|---------------------|
| Andon (stop-the-line) | Confidence thresholds triggering pause |
| Poka-yoke (error-proofing) | Input validation, output constraints |
| Self-quality check | Self-evaluation before output delivery |
| Human intervention | Escalation pathways to operators |

### Concrete Implementations

```python
class JidokaAgent:
    def execute(self, task):
        # Step 1: Attempt with self-monitoring
        result = self.generate_with_monitoring(task)
        
        # Step 2: Self-quality check (built-in, not bolted-on)
        quality_score = self.evaluate_output(result, task)
        
        # Step 3: Decision based on quality
        if quality_score > 0.9:
            return result  # Autonomous completion
        elif quality_score > 0.6:
            return self.self_correct(result, task)  # Retry
        else:
            return self.escalate_to_human(task, result)  # Andon pull
    
    def evaluate_output(self, result, task):
        """Self-check: Does output meet requirements?"""
        checks = [
            self.check_format_compliance(result),
            self.check_factual_consistency(result),
            self.check_task_completion(result, task),
            self.check_safety_constraints(result)
        ]
        return sum(checks) / len(checks)
```

**Jidoka Patterns for Agents:**

1. **Confidence-Based Routing**
   - High confidence (>0.9): Auto-execute
   - Medium confidence (0.6-0.9): Self-verify and retry
   - Low confidence (<0.6): Human review queue

2. **Real-Time Monitoring Dashboard**
   ```
   Agent Status: EXECUTING
   Task: Process refund request
   Confidence: 0.45 ↓ (DROPPING)
   [STOP] [ESCALATE] [OVERRIDE]
   ```

3. **Circuit Breakers**
   - Detect repeated failures → Pause and alert
   - Anomaly detection on output patterns
   - Resource usage limits (prevent runaway costs)

---

## 3. Kaizen (Continuous Improvement) → Self-Evolving Agent Loops

### TPS Principle
**Continuous, incremental improvement by all members.**
- Small, frequent improvements compound over time
- Standardize → Improve → Standardize
- Everyone participates in improvement

### AI Agent Equivalent
**Self-improving agents that learn from every interaction.**

| TPS Concept | Agent Implementation |
|-------------|---------------------|
| PDCA cycle (Plan-Do-Check-Act) | Prompt evaluation → Execution → Review → Update |
| Standard work | Versioned prompt templates |
| Improvement suggestions | Feedback loop for prompt optimization |
| Gemba walks | Trace analysis and bottleneck identification |

### Concrete Implementations

```python
class KaizenAgent:
    def __init__(self):
        self.prompt_registry = PromptRegistry()
        self.feedback_log = []
        
    def execute_and_learn(self, task):
        # PLAN: Select best prompt version
        prompt = self.prompt_registry.get_best_prompt(task.type)
        
        # DO: Execute
        result = self.llm.generate(prompt, task)
        
        # CHECK: Gather feedback (explicit + implicit)
        feedback = self.collect_feedback(result, task)
        self.feedback_log.append(feedback)
        
        # ACT: Trigger improvement if warranted
        if self.should_optimize():
            self.evolve_prompts()
        
        return result
    
    def evolve_prompts(self):
        """Auto-improve based on accumulated feedback."""
        # Analyze failures
        failures = [f for f in self.feedback_log if not f.success]
        patterns = self.identify_failure_patterns(failures)
        
        # Generate improved prompts
        for pattern in patterns:
            new_prompt = self.generate_improved_prompt(pattern)
            self.prompt_registry.add_variant(new_prompt)
            
        # A/B test new variants
        self.prompt_registry.start_experiment(patterns)
```

**Kaizen Mechanisms:**

| Mechanism | Implementation |
|-----------|---------------|
| **Prompt A/B Testing** | Route 10% traffic to new prompt variants |
| **Failure Pattern Mining** | Cluster unsuccessful outcomes, find root causes |
| **Success Amplification** | Identify winning patterns, propagate to other agents |
| **Meta-Learning** | Learn which prompt structures work for which task types |
| **Auto-Evaluation** | Synthetic test cases to validate improvements |

**Self-Improvement Loop:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EXECUTE   │───→│   MEASURE   │───→│   ANALYZE   │
│   (Do)      │    │   (Check)   │    │   (Plan)    │
└─────────────┘    └─────────────┘    └──────┬──────┘
       ↑                                      │
       └──────────────────────────────────────┘
                    (Act - Deploy improvement)
```

---

## 4. Genchi Genbutsu (Go See) → Real-World Validation Before Deployment

### TPS Principle
**Go to the source to see the actual situation.**
- Don't rely on reports, see the actual process
- Understand the real problem through direct observation
- Validate assumptions at the gemba (actual place)

### AI Agent Equivalent
**Test in realistic environments before production deployment.**

| TPS Concept | Agent Implementation |
|-------------|---------------------|
| Gemba (actual place) | Production-like staging environment |
| Direct observation | Tracing and logging actual behavior |
| 5 Whys analysis | Root cause analysis of failures |
| Validation at source | Shadow mode deployment |

### Concrete Implementations

```python
class GenchiGenbutsuDeployment:
    """
    Deployment pipeline that validates in realistic conditions
    before full rollout.
    """
    
    def deploy_agent(self, agent_version):
        # Phase 1: Synthetic validation (lab conditions)
        synthetic_results = self.test_on_synthetic_data(agent_version)
        if not self.meets_quality_bar(synthetic_results):
            return "REJECT: Fails synthetic tests"
        
        # Phase 2: Shadow mode (observe without affecting)
        # Run new agent in parallel, compare to production
        shadow_results = self.run_shadow_mode(agent_version, duration="7d")
        divergence = self.measure_divergence(shadow_results, production_results)
        if divergence > 0.05:  # 5% difference threshold
            return "REJECT: Shadow mode divergence too high"
        
        # Phase 3: Canary deployment (limited real exposure)
        canary_results = self.canary_deploy(agent_version, traffic=0.01)
        if not self.monitor_health(canary_results):
            return "ROLLBACK: Health checks failed"
        
        # Phase 4: Full deployment
        self.full_rollout(agent_version)
        return "DEPLOYED"
```

**Go-See Validation Techniques:**

1. **Shadow Mode**
   - New agent processes real requests
   - Outputs logged but not returned to user
   - Compare: New vs. Production consistency

2. **Replay Testing**
   - Record production traffic
   - Replay against new agent version
   - Detect regressions in known cases

3. **Adversarial Testing**
   - Test edge cases found in production
   - Red-team with actual failure patterns
   - Validate robustness to real noise

4. **User Journey Validation**
   ```
   Real user request → Staging agent → Log result
   Real user request → Production agent → Return to user
   
   Daily: Compare staging vs. production outcomes
   ```

---

## 5. Muda (Waste) → Token Waste, Compute Waste, Context Window Waste

### TPS Principle
**Eliminate waste in all its forms — activities that don't add value.**
- 7 Wastes: Overproduction, Waiting, Transport, Over-processing, Inventory, Motion, Defects

### AI Agent Equivalent
**Eliminate computational waste that doesn't improve output quality.**

| TPS Waste | AI Agent Equivalent | Detection | Elimination |
|-----------|---------------------|-----------|-------------|
| **Overproduction** | Generating unused tokens | Log token consumption per request | Early stopping, confidence thresholds |
| **Waiting** | Idle context in window | Measure context utilization | Sliding window, relevance filtering |
| **Transport** | Unnecessary data movement | Track data copies/transfers | In-context retrieval, lazy loading |
| **Over-processing** | Using oversized models | Model size vs. task complexity | Model cascading, task routing |
| **Inventory** | Stale context/history | Age of context items | Time-decay weighting, auto-summarization |
| **Motion** | Redundant API calls | Call frequency analysis | Batching, caching, memoization |
| **Defects** | Hallucinations/errors | Error rate tracking | Self-correction, validation layers |

### Concrete Implementations

```python
class LeanAgent:
    """Agent designed to minimize computational waste."""
    
    # === WASTE TYPE 1: Token Overproduction ===
    def generate_concise(self, prompt, max_useful_tokens=500):
        """Generate only what's needed."""
        # Start with small max_tokens
        for budget in [100, 250, 500, 1000]:
            result = self.llm.generate(prompt, max_tokens=budget)
            if self.is_complete(result):
                return result
        return result  # Full budget if needed
    
    # === WASTE TYPE 2: Context Window Waste ===
    def maintain_lean_context(self, conversation_history):
        """Keep only valuable context."""
        # Remove: Redundant messages
        history = self.deduplicate_messages(conversation_history)
        
        # Summarize: Old turns beyond relevance window
        old_messages = history[:-5]  # Keep last 5 full
        summary = self.summarize(old_messages)
        
        # Prioritize: Rank by relevance to current query
        ranked = self.rank_by_relevance(history[-5:])
        
        return [summary] + ranked[:5]
    
    # === WASTE TYPE 3: Compute Over-processing ===
    def route_to_appropriate_model(self, task):
        """Right-size the model for the task."""
        complexity = self.assess_complexity(task)
        
        routing_table = {
            "trivial": "gpt-3.5-turbo",      # Cheap, fast
            "standard": "claude-sonnet",      # Balanced
            "complex": "gpt-4",               # Capable
            "research": "claude-opus"         # Most capable
        }
        
        return routing_table.get(complexity, "claude-sonnet")
    
    # === WASTE TYPE 4: Redundant Computation ===
    @functools.lru_cache(maxsize=1000)
    def cached_embedding(self, text):
        """Don't recompute embeddings."""
        return self.embedding_model.encode(text)
    
    # === WASTE TYPE 5: Hallucination Defects ===
    def verify_before_output(self, result, sources):
        """Catch defects before delivery."""
        claims = self.extract_claims(result)
        for claim in claims:
            if not self.verify_against_sources(claim, sources):
                result = self.flag_or_correct(result, claim)
        return result
```

**Waste Dashboard Metrics:**

```yaml
Token Waste:
  - Over-generation rate: 15% (target: <5%)
  - Prompt padding waste: 23% (target: <10%)
  - Unused completion tokens: 12%

Compute Waste:
  - Model oversized for task: 34% of calls
  - Redundant embeddings: 45% cache miss
  - Idle context slots: 40% of window

Quality Waste (Defects):
  - Hallucination rate: 2.1% (target: <1%)
  - Self-correction triggers: 8%
  - Human escalation rate: 5%
```

---

## Synthesis: Lean Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LEAN AGENT SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   INPUT     │→ │   ROUTER    │→ │    JIT      │         │
│  │   LAYER     │  │ (Complexity)│  │  PROMPTER   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         ↓                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   LEAN      │→ │   JIDOKA    │→ │   OUTPUT    │         │
│  │   CONTEXT   │  │   CHECK     │  │   GATE      │         │
│  │  MANAGER    │  │ (Quality)   │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         ↑              ↓                    ↓               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   KAIZEN    │  │  HUMAN      │  │   GENCHI    │         │
│  │   ENGINE    │  │  ESCALATION │  │   VALIDATE  │         │
│  │ (Improve)   │  │  (Andon)    │  │  (Shadow)   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              WASTE MONITORING DASHBOARD              │   │
│  │  • Token utilization    • Compute efficiency         │   │
│  │  • Context density      • Cache hit rates            │   │
│  │  • Error rates          • Cost per task              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Metrics for Lean AI

| Metric | TPS Analogy | Target |
|--------|-------------|--------|
| Token Efficiency | Material yield | >80% of tokens add value |
| Context Density | Inventory turns | >70% of window actively used |
| Model Right-Sizing | Resource allocation | <10% over-provisioning |
| First-Pass Yield | Quality at source | >95% no self-correction needed |
| Escalation Rate | Andon pulls | <5% require human intervention |
| Improvement Velocity | Kaizen frequency | >1 prompt update per week |

---

## Implementation Roadmap

### Phase 1: Measure (Weeks 1-2)
- Instrument agents to track waste metrics
- Establish baseline for token/compute usage
- Identify biggest waste sources

### Phase 2: JIT + Muda (Weeks 3-6)
- Implement lazy context loading
- Add model cascading
- Deploy token optimization

### Phase 3: Jidoka (Weeks 7-10)
- Add confidence scoring
- Build escalation pathways
- Implement self-correction loops

### Phase 4: Kaizen (Weeks 11-14)
- Deploy prompt A/B testing
- Build feedback collection
- Automate improvement suggestions

### Phase 5: Genchi Genbutsu (Ongoing)
- Shadow mode for all major changes
- Replay testing suite
- Production-like staging validation

---

> *"The best AI agent is one that delivers maximum value with minimum waste, stopping gracefully when uncertain, and improving continuously from every interaction."*

**Reference Implementation**: See `/skills/lean-agent/` for reusable components.
