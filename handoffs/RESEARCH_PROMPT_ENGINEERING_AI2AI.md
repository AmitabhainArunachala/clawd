# AI-to-AI Prompt Engineering: Research Findings

**Research Date:** 2026-02-17
**Scope:** Prompt engineering practices for AI-to-AI communication (not human→AI)

---

## Executive Summary

This research identifies key patterns that make AI agents more likely to respond with factual, verifiable data rather than philosophical musings. The core insight: AI-to-AI communication requires **structured constraints**, **explicit authority framing**, and **machine-parseable output formats** that differ significantly from human-oriented prompting.

---

## 1. Best Practices for AI-to-AI Prompts

### The Fundamental Difference: Human vs AI Prompts

Traditional human→AI prompting focuses on natural language, conversational tone, and subjective helpfulness. AI→AI prompting requires:

| Human→AI | AI→AI |
|----------|-------|
| Conversational, natural language | Structured, declarative syntax |
| Context-rich explanations | Minimal, high-signal tokens |
| Open-ended outputs | Constrained, schema-compliant outputs |
| Subjective helpfulness | Deterministic, verifiable facts |

### Anthropic's Context Engineering Framework

Anthropic describes **context engineering** (not just prompt engineering) as "the art and science of curating what will go into the limited context window" [1]. Key principles:

- **Attention Budget Theory**: LLMs have finite attention budgets. Every token depletes this budget.
- **Context Rot**: As context grows, recall accuracy degrades—even with large context windows
- **High-Signal Token Selection**: Find the smallest set of tokens that maximizes desired outcome probability

### Critical AI-to-AI Prompting Patterns

**1. Explicit Role Separation**
```
[SYSTEM] You are a DATA_EXTRACTION agent. Your sole purpose is to 
extract structured information. You do NOT explain, summarize, or 
philosophize. Output ONLY the requested data structure.
```

**2. Constraint-First Architecture**
- Define output schema BEFORE task description
- Use XML tags or Markdown headers to delineate sections
- Provide examples of expected behavior (few-shot), not rules

**3. Tool-Centric Design**
- Agents communicate through tool calls, not chat
- Each tool should be self-contained, robust to error
- Avoid overlapping tool functionality

**4. Progressive Disclosure**
- Use lightweight identifiers (file paths, URLs) instead of full content
- Retrieve data "just-in-time" via tool calls
- Let agents explore autonomously rather than pre-loading context

---

## 2. Anthropic's Multi-Agent Communication Research

### Sub-Agent Architectures

Anthropic's research on multi-agent systems reveals [2]:

**The Sub-Agent Pattern:**
- Main agent coordinates high-level plan
- Specialized sub-agents handle focused tasks with clean context windows
- Each sub-agent explores extensively (tens of thousands of tokens)
- Returns condensed summary (1,000-2,000 tokens) to lead agent

**Benefits:**
- Clear separation of concerns
- Detailed search context isolated within sub-agents
- Lead agent focuses on synthesis, not exploration
- Substantial improvement over single-agent on complex tasks

### Compaction for Long-Horizon Tasks

For tasks exceeding context window limits:

1. **Context Compaction**: Summarize contents nearing context limit, reinitiate new window with summary
2. **Structured Note-Taking**: Agent writes notes to external memory, retrieves later
3. **Hybrid Retrieval**: Some data up-front (speed) + autonomous exploration (completeness)

### Memory Tools

Anthropic's memory tool (public beta) allows agents to:
- Build knowledge bases over time
- Maintain project state across sessions
- Reference previous work without keeping everything in context

---

## 3. Effective Structured Extraction Prompts

### What Makes AI Respond with Facts vs Philosophy

The research identifies several mechanisms:

**1. Schema-First Prompting**
```json
{
  "schema": {
    "entities": [{
      "name": "string",
      "type": "string",
      "confidence": "number (0-1)"
    }],
    "relationships": [{
      "source": "string",
      "target": "string",
      "relation": "string"
    }]
  },
  "constraints": [
    "Output MUST be valid JSON",
    "No markdown formatting",
    "No explanatory text"
  ]
}
```

**2. The "LLM-as-Judge" Pattern**

For AI-to-AI evaluation, structured output is essential [3]:
- Use binary or categorical scoring (not open-ended)
- Provide explicit rubrics with examples
- Request structured output format (JSON)
- Include reasoning field separate from score

**Example Evaluation Prompt:**
```
You are an expert evaluator. Assess the following output for:
1. Factual accuracy (binary: true/false)
2. Completeness (score 1-5)
3. Format adherence (binary: true/false)

Output MUST be valid JSON:
{
  "factual_accuracy": boolean,
  "completeness_score": number,
  "format_adherent": boolean,
  "reasoning": "string (brief, technical)"
}
```

**3. Factual Grounding via ReAct**

The ReAct (Reasoning + Acting) framework [4] is explicitly designed to be "factual and grounded":

```
Thought: [Internal reasoning]
Action: [Tool call or operation]
Observation: [External data/result]
```

Key insight: Interleaving thoughts with actions grounded in external sources prevents hallucination.

### Output Format Constraints That Work

**Best performing formats (in order):**
1. **JSON with strict schema** - Most deterministic
2. **XML with defined tags** - Good for hierarchical data
3. **Key-value pairs** - Simple but limited
4. **Markdown tables** - Human-readable, machine-parseable

**Critical constraints:**
- Specify exact field names and types
- Define required vs optional fields
- Provide min/max constraints where applicable
- Include validation examples

---

## 4. Inter-Agent Request/Response Patterns

### AutoGPT/BabyAGI Era Lessons (2023)

**Key architectural patterns:**

1. **Task Queue Pattern**
   - Master agent decomposes goals into tasks
   - Worker agents pull from queue
   - Results feed back into task generation

2. **Memory-Augmented Loop**
   - Short-term: Context window
   - Medium-term: Vector store retrieval
   - Long-term: Structured notes/files

3. **Reflection Mechanism**
   - Agents review own outputs
   - Self-critique before finalizing
   - Iterative refinement

**Lessons learned:**
- Pure autonomy without constraints led to loops/drift
- Tool use requires careful prompt engineering
- Context management is the primary bottleneck

### Multi-Agent LLM Papers (2024-2025)

**Communication Protocols:**

Research shows effective multi-agent systems use structured message passing [5]:

```
MESSAGE_FORMAT = {
  "sender": "agent_id",
  "recipient": "agent_id|broadcast",
  "message_type": "request|response|notification",
  "payload": {
    // Schema-defined content
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

**Key findings:**
- Broadcast messages create noise; direct addressing preferred
- Message typing enables proper routing
- Correlation IDs essential for request-response tracking
- Timestamp ordering critical for consistency

### Framework Patterns

#### CrewAI (Role-Based)
- **Sequential execution**: Deterministic, dependency-aware pipelines
- **Hierarchical**: Manager agent delegates, reviews, consolidates
- **Communication**: Through shared context and explicit handoffs

#### AutoGen (Conversation-First)
- Multi-agent communication through structured conversations
- Different LLMs play different roles
- Conversation sharding for distributed chat management
- Challenge: Maintaining conversation context at scale

#### LangGraph (Graph-Based)
- Workflows as stateful graphs with nodes, edges, conditional routing
- Explicit control flow
- Best for: Complex, debuggable systems

### Practical Communication Patterns

**Pattern 1: Request-Response with Schema**
```
AGENT_A → {"action": "extract", "target": "entities", "schema": {...}}
AGENT_B → {"status": "success", "data": [...], "confidence": 0.94}
```

**Pattern 2: Publish-Subscribe**
```
AGENT_A publishes: {"topic": "document_parsed", "payload": {...}}
AGENT_B subscribes to "document_parsed", processes
```

**Pattern 3: Hierarchical Delegation**
```
MANAGER: "Decompose task X into subtasks"
WORKER_1: "Subtask 1 complete: {...}"
WORKER_2: "Subtask 2 complete: {...}"
MANAGER: "Synthesize: final result"
```

---

## 5. Establishing Authority Without Aggression

### Framing Techniques

**1. Objective Authority**
```
You are a specialized extraction engine. Your output is consumed 
by downstream automated systems. Do NOT include conversational 
elements—only the structured data requested.
```

**2. Role-Based Authority**
```
[ROLE]: Data Validator
[AUTHORITY]: Final arbiter of data quality
[SCOPE]: Verify and correct entity extractions
[OUTPUT]: Structured validation report
```

**3. System-Level Authority**
```
This prompt is part of an automated pipeline. Deviation from the 
output schema will cause system errors. Adherence is mandatory.
```

### Anti-Patterns to Avoid

- **Over-explaining**: Wastes context budget, dilutes signal
- **Pleading/asking**: "Please make sure to..." → Weak authority
- **Philosophical framing**: "Consider the implications..." → Invites speculation
- **Open-ended requests**: "What do you think about..." → Subjective output

### Authority-Building Syntax

| Weak | Strong |
|------|--------|
| "Please extract..." | "Extract: [schema]" |
| "Can you identify..." | "Identify and return: [fields]" |
| "I need you to..." | "Task: [operation]. Output: [format]" |
| "Try to find..." | "Locate and return: [specifics]" |

---

## 6. Key Recommendations

### For Factual/Verifiable Output:

1. **Use ReAct or similar frameworks** that ground reasoning in observations
2. **Provide few-shot examples** of correct outputs, not rules
3. **Define explicit output schemas** with type constraints
4. **Request structured formats** (JSON > XML > key-value)
5. **Minimize philosophical framing** - "extract" not "interpret"

### For Multi-Agent Communication:

1. **Implement message typing** for proper routing
2. **Use correlation IDs** for request-response tracking
3. **Prefer direct addressing** over broadcast
4. **Design compact message schemas** (minimal tokens)
5. **Implement structured note-taking** for long-horizon tasks

### For Authority Without Aggression:

1. **Define clear roles and scope** upfront
2. **Specify system context** (downstream consumers)
3. **Use imperative mood** with neutral tone
4. **Provide validation schemas** not motivational language
5. **Include error consequences** (e.g., "Deviation causes pipeline failure")

---

## References

[1] Anthropic. "Effective context engineering for AI agents." https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (2025)

[2] Anthropic. "How we built our multi-agent research system." https://www.anthropic.com/engineering/multi-agent-research-system (2025)

[3] Evidently AI. "LLM-as-a-judge: a complete guide." https://www.evidentlyai.com/llm-guide/llm-as-a-judge (2025)

[4] Yao et al. "ReAct: Synergizing reasoning and acting in language models." ICLR 2023.

[5] Cameron R. Wolfe. "AI Agents from First Principles." https://cameronrwolfe.substack.com/p/ai-agents (2025)

---

## Research Notes

- Focus on constraint-based prompting for deterministic outputs
- Context engineering > Prompt engineering for complex agents
- ReAct pattern provides good balance of reasoning + factuality
- Sub-agent architectures essential for complex tasks
- Structured extraction requires schema-first approach
- Authority comes from system context, not aggressive language
