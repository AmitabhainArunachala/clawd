# Multi-Agent Orchestration Frameworks Deep Research (2026)

## Executive Summary

This research compares six major multi-agent orchestration frameworks—**CrewAI, LangGraph, AutoGen, OpenAI Agents SDK (formerly Swarm), AgentVerse, and MetaGPT**—with focus on scaling to 100+ concurrent agents for a "dharmic swarm" architecture.

**Key Finding:** No single framework perfectly handles 100 concurrent agents out-of-box. The optimal approach is a **hybrid architecture** combining AutoGen Core (for distributed runtime) + CrewAI (for agent orchestration patterns) + custom memory layer.

---

## Framework Comparison Matrix

| Feature | CrewAI | LangGraph | AutoGen | OpenAI Agents SDK | AgentVerse | MetaGPT |
|---------|--------|-----------|---------|-------------------|------------|---------|
| **100 Agent Scaling** | ⚠️ Sequential | ⚠️ Limited | ✅ Distributed | ⚠️ Stateless | ✅ Simulation | ⚠️ Sequential |
| **Communication** | Role-based | Graph edges | Pub/Sub + Direct | Handoffs only | Env-based | SOP-based |
| **Memory Sharing** | ✅ RAG + SQLite | ✅ State checkpoints | ✅ Custom stores | ⚠️ Session-based | Limited | Limited |
| **Task Decomposition** | ✅ Hierarchical | ✅ Subgraphs | ✅ Teams | ✅ Handoffs | ✅ Multi-agent | ✅ Role-based |
| **Distributed Runtime** | ❌ | ❌ | ✅ gRPC | ❌ | ❌ | ❌ |
| **Production Ready** | ✅ | ✅ | ✅ | ✅ | ⚠️ Research | ⚠️ |
| **Provider Agnostic** | ✅ LiteLLM | ✅ LangChain | ✅ Extensions | ✅ 100+ LLMs | ⚠️ OpenAI | ⚠️ |

---

## Detailed Framework Analysis

### 1. CrewAI

**Philosophy:** "Agents as a Crew" - Collaborative teams with defined roles

**Strengths:**
- Most intuitive mental model (Agents → Tasks → Crews → Flows)
- Excellent state management with @persist decorator
- RAG-based memory (Short-term, Long-term, Entity)
- Event-driven Flows with @start(), @listen(), @router()
- YAML config for agent definitions

**For 100 Agents:**
```python
# CrewAI approach - hierarchical decomposition
from crewai import Agent, Crew, Process, Flow

# Create specialized sub-crews
research_crew = Crew(agents=research_agents[:10], process=Process.parallel)
analysis_crew = Crew(agents=analysis_agents[:10], process=Process.parallel)

# Orchestrate with Flows
class SwarmFlow(Flow):
    @start()
    def dispatch_research(self):
        # Parallelize across crews
        return [research_crew.kickoff_async() for _ in range(10)]
    
    @listen(dispatch_research)
    def aggregate_results(self, results):
        # Reduce pattern
        pass
```

**Limitations for 100 Agents:**
- No native distributed runtime
- Sequential by default (parallel requires careful orchestration)
- Memory contention with many concurrent RAG queries

---

### 2. LangGraph (LangChain)

**Philosophy:** "Agents as Graphs" - State machines with durable execution

**Strengths:**
- Pregel/Apache Beam-inspired architecture
- Durable execution - survives failures, resumes from checkpoints
- Human-in-the-loop with interrupts
- Deep LangSmith integration for debugging
- Comprehensive memory (short-term + long-term + cross-session)

**For 100 Agents:**
```python
from langgraph.graph import StateGraph, MessagesState

# Subgraph pattern for scaling
def create_agent_subgraph(agent_id):
    graph = StateGraph(MessagesState)
    graph.add_node("think", think_node)
    graph.add_node("act", act_node)
    return graph.compile()

# Parent graph orchestrates 100 subgraphs
master_graph = StateGraph(SwarmState)
for i in range(100):
    master_graph.add_node(f"agent_{i}", create_agent_subgraph(i))
```

**Limitations for 100 Agents:**
- Single-threaded by default
- State explosion with large agent counts
- No native distributed execution

---

### 3. AutoGen (Microsoft)

**Philosophy:** "Event-driven agent runtime" - Scalable, distributed multi-agent systems

**Strengths for 100 Agents:** ⭐ BEST CHOICE FOR DISTRIBUTED
- **GrpcWorkerAgentRuntime** - Native distributed execution across machines
- Publish/Subscribe messaging + Direct messaging
- Event-driven architecture (not sequential)
- Separate packages: Core (scalable), AgentChat (easy), Studio (no-code)
- Agent lifecycle managed by runtime (not application code)

**100 Concurrent Agents Architecture:**
```python
from autogen_core import (
    SingleThreadedAgentRuntime,
    RoutedAgent, 
    message_handler,
    AgentId
)
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime

# For distributed: Use GrpcWorkerAgentRuntime
runtime = GrpcWorkerAgentRuntime(host_address="localhost:50051")

# Register 100 agent types
for i in range(100):
    await DharmicAgent.register(
        runtime, 
        f"dharmic_agent_{i}",
        lambda: DharmicAgent(role=f"worker_{i}")
    )

# Publish message to all agents (fan-out)
await runtime.publish_message(
    TaskMessage("analyze this"),
    topic_id=TopicId("dharma_topic", "source")
)

# Start processing
runtime.start()
await runtime.stop_when_idle()
```

**Communication Patterns:**
1. **Direct Message**: `runtime.send_message(msg, AgentId("type", "instance"))`
2. **Publish/Subscribe**: `runtime.publish_message(msg, TopicId(...))`
3. **Broadcast**: Via topic subscriptions

**Memory Sharing (Custom):**
```python
# AutoGen doesn't prescribe memory - bring your own
from redis import Redis

class SharedMemoryMixin:
    def __init__(self):
        self.redis = Redis()
    
    async def share_insight(self, key, value):
        self.redis.hset("swarm_memory", key, json.dumps(value))
    
    async def get_collective_memory(self):
        return self.redis.hgetall("swarm_memory")
```

---

### 4. OpenAI Agents SDK (Successor to Swarm)

**Philosophy:** "Lightweight, stateless orchestration"

**Key Concepts:**
- Agents with instructions + tools + handoffs
- Handoffs = specialized tool calls for agent-to-agent transfer
- Sessions for conversation history (SQLite, Redis)
- Guardrails for input/output validation
- Provider-agnostic (100+ LLMs via LiteLLM)

**For 100 Agents:**
```python
from agents import Agent, Runner
import asyncio

# Define agents with handoff capability
agents = [
    Agent(
        name=f"Worker_{i}",
        instructions=f"You handle domain {i}",
        handoffs=[agent_coordinator]  # Can transfer back
    ) for i in range(100)
]

# Coordinator routes to workers
coordinator = Agent(
    name="Coordinator",
    instructions="Route tasks to appropriate workers",
    handoffs=agents
)

# Parallel execution
async def run_swarm(tasks):
    return await asyncio.gather(*[
        Runner.run(coordinator, task) for task in tasks
    ])
```

**Limitations:**
- Stateless between runs (by design)
- Handoff is sequential (agent A → agent B), not parallel
- No native pub/sub or broadcast

---

### 5. AgentVerse (OpenBMB)

**Philosophy:** "Multi-agent simulation and task-solving"

**Two Frameworks:**
1. **Task-Solving**: Auto multi-agent collaboration (software dev, consulting)
2. **Simulation**: Observable multi-agent environments (games, research)

**Strengths for 100 Agents:**
- Designed for multi-agent simulation with many participants
- Environment-based communication (agents observe environment)
- CLI + GUI for visualization
- Research-oriented (ICLR 2024)

**For 100 Agents:**
```yaml
# agentverse/tasks/simulation/config.yaml
agents:
  - name: dharmic_agent_{i}
    role: worker
    llm: gpt-4o
    
environment:
  type: simulation_env
  max_agents: 100
  communication: broadcast
```

**Limitations:**
- More research than production
- Tightly coupled to environment metaphor
- Less flexible for arbitrary workflows

---

### 6. MetaGPT

**Philosophy:** "SOP-driven multi-agent software company"

**Core Concept:** `Code = SOP(Team)`
- Roles: PM, Architect, Engineer, QA
- Standardized operating procedures
- Automatic document generation

**For 100 Agents:**
```python
from metagpt.roles import Role
from metagpt.team import Team

# Define custom roles for swarm
class DharmicWorker(Role):
    name: str = "Worker"
    goal: str = "Execute dharmic task"
    
# Team of 100 (theoretically)
team = Team()
for i in range(100):
    team.hire(DharmicWorker(name=f"Worker_{i}"))
```

**Limitations:**
- Designed for software development workflow
- Sequential SOP execution
- Not optimized for general swarm patterns

---

## Running 100 Concurrent Agents: Technical Approaches

### Approach 1: Process-Level Parallelism (Simple)
```python
import multiprocessing
from crewai import Agent, Crew

def run_agent_batch(agent_ids):
    agents = [create_agent(id) for id in agent_ids]
    crew = Crew(agents=agents, process=Process.parallel)
    return crew.kickoff()

# 10 processes × 10 agents each = 100 concurrent
with multiprocessing.Pool(10) as pool:
    results = pool.map(run_agent_batch, chunks(range(100), 10))
```

### Approach 2: Async Concurrency (Better)
```python
import asyncio
from agents import Agent, Runner

async def dharmic_swarm(task, num_agents=100):
    agents = [Agent(name=f"dharmic_{i}") for i in range(num_agents)]
    
    async def run_agent(agent, subtask):
        return await Runner.run(agent, subtask)
    
    # True concurrent execution
    subtasks = decompose_task(task, num_agents)
    results = await asyncio.gather(*[
        run_agent(a, t) for a, t in zip(agents, subtasks)
    ])
    
    return aggregate(results)
```

### Approach 3: Distributed Runtime (Production)
```python
# AutoGen with gRPC for true distribution
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime

# Machine 1: Coordinator
coordinator_runtime = GrpcWorkerAgentRuntime(
    host_address="0.0.0.0:50051"
)

# Machines 2-11: Workers (10 agents each)
worker_runtime = GrpcWorkerAgentRuntime(
    host_address="worker_n:50051"
)
for i in range(10):
    await WorkerAgent.register(worker_runtime, f"worker_{i}")
```

---

## Communication Patterns for 100 Agents

### 1. Hub-and-Spoke (Coordinator Pattern)
```
       ┌─────────────────┐
       │   Coordinator   │
       └────────┬────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│Agent 1│  │Agent 2│  │Agent N│
└───────┘  └───────┘  └───────┘
```
**Use:** Task distribution, result aggregation
**Frameworks:** All support this pattern

### 2. Publish-Subscribe (Broadcast)
```
┌─────────────────────────────────┐
│           Message Bus           │
└──────────────┬──────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│Agent 1│  │Agent 2│  │Agent N│
└───────┘  └───────┘  └───────┘
```
**Use:** Announcements, state sync
**Frameworks:** AutoGen (native), others (custom)

### 3. Mesh/P2P (Decentralized)
```
┌───────┐     ┌───────┐
│Agent 1│◄───►│Agent 2│
└───┬───┘     └───┬───┘
    │             │
    └──────┬──────┘
           │
       ┌───▼───┐
       │Agent N│
       └───────┘
```
**Use:** Emergent collaboration
**Frameworks:** AgentVerse (simulation), custom implementations

### 4. Hierarchical (Tree)
```
            ┌──────────┐
            │  Leader  │
            └────┬─────┘
         ┌───────┼───────┐
    ┌────▼───┐       ┌───▼────┐
    │Manager1│       │Manager2│
    └────┬───┘       └───┬────┘
    ┌────┼────┐     ┌────┼────┐
┌───▼┐┌─▼─┐┌─▼─┐ ┌─▼─┐┌─▼─┐┌─▼─┐
│W1  ││W2 ││W3 │ │W4 ││W5 ││W6 │
└────┘└───┘└───┘ └───┘└───┘└───┘
```
**Use:** Task decomposition, result aggregation
**Frameworks:** CrewAI (hierarchical process), MetaGPT

---

## Memory Sharing Patterns

### Pattern 1: Shared RAG Store
```python
# All agents share same ChromaDB collection
from crewai import Crew

crew = Crew(
    agents=agents_100,
    memory=True,  # Shared RAG
    embedder={"provider": "ollama", "model": "mxbai-embed-large"}
)
```

### Pattern 2: Redis Pub/Sub for Real-time Sync
```python
import redis.asyncio as redis

class SharedBrain:
    def __init__(self):
        self.r = redis.Redis()
        self.pubsub = self.r.pubsub()
    
    async def broadcast_insight(self, insight):
        await self.r.publish("swarm_channel", json.dumps(insight))
    
    async def listen_to_swarm(self, handler):
        await self.pubsub.subscribe("swarm_channel")
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                await handler(json.loads(message['data']))
```

### Pattern 3: Event Sourcing (Append-only Log)
```python
# Every agent action is an event
class SwarmEventStore:
    def __init__(self):
        self.events = []  # Or Kafka/Redis Streams
    
    def append(self, agent_id, event_type, payload):
        self.events.append({
            "timestamp": time.time(),
            "agent": agent_id,
            "type": event_type,
            "data": payload
        })
    
    def replay(self, from_timestamp=0):
        return [e for e in self.events if e["timestamp"] >= from_timestamp]
```

### Pattern 4: Blackboard Architecture
```python
class Blackboard:
    """Shared workspace where agents post and read insights"""
    
    def __init__(self):
        self.knowledge = {}  # Domain → Facts
        self.hypotheses = []
        self.solutions = []
    
    def post(self, agent_id, category, content):
        self.knowledge.setdefault(category, []).append({
            "author": agent_id,
            "content": content,
            "timestamp": time.time()
        })
    
    def query(self, category, limit=10):
        return self.knowledge.get(category, [])[-limit:]
```

---

## Task Decomposition Strategies

### 1. Map-Reduce Pattern
```python
# 1 task → 100 subtasks → 100 results → 1 final result
async def map_reduce_swarm(task, agents):
    # MAP: Decompose and distribute
    subtasks = await coordinator.decompose(task, len(agents))
    
    # EXECUTE: Parallel processing
    results = await asyncio.gather(*[
        agent.execute(subtask) 
        for agent, subtask in zip(agents, subtasks)
    ])
    
    # REDUCE: Aggregate results
    return await coordinator.aggregate(results)
```

### 2. Recursive Decomposition (Divide & Conquer)
```python
async def recursive_swarm(task, agents, depth=0, max_depth=3):
    if depth >= max_depth or len(agents) == 1:
        return await agents[0].execute(task)
    
    # Split task and agents
    subtasks = await decomposer.split(task, 2)
    mid = len(agents) // 2
    
    # Recursive parallel execution
    left_result, right_result = await asyncio.gather(
        recursive_swarm(subtasks[0], agents[:mid], depth+1),
        recursive_swarm(subtasks[1], agents[mid:], depth+1)
    )
    
    return await merger.combine(left_result, right_result)
```

### 3. Specialist Routing
```python
# Route to specialist agents based on task type
class SpecialistRouter:
    def __init__(self, specialists: dict[str, list[Agent]]):
        self.specialists = specialists  # {"code": [...], "research": [...]}
    
    async def route(self, task):
        task_type = await self.classifier.classify(task)
        available_agents = self.specialists[task_type]
        return random.choice(available_agents)  # Or load-balance
```

---

## Dharmic Swarm Architecture (100 Agents)

### Design Principles
1. **Ahimsa (Non-violence)**: Agents don't compete, they collaborate
2. **Satya (Truth)**: Shared memory ensures consistent world-view
3. **Dharma (Purpose)**: Each agent has clear, non-overlapping purpose
4. **Karma (Action)**: Every action is logged, traceable, accountable
5. **Seva (Service)**: Agents serve the collective, not individual goals

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DHARMIC SWARM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    COORDINATION LAYER                    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │ Dharma   │ │ Task     │ │ Memory   │ │ Karma    │    │   │
│  │  │ Keeper   │ │ Decomp.  │ │ Guardian │ │ Logger   │    │   │
│  │  │ (1 agent)│ │ (1 agent)│ │ (1 agent)│ │ (1 agent)│    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                               │                                 │
│                               ▼                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    MESSAGE BUS (Redis Streams)           │   │
│  └─────────────────────────────────────────────────────────┘   │
│       │              │              │              │            │
│       ▼              ▼              ▼              ▼            │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │ Sangha 1│    │ Sangha 2│    │ Sangha 3│    │ Sangha N│     │
│  │ (25     │    │ (25     │    │ (25     │    │ (25     │     │
│  │ workers)│    │ workers)│    │ workers)│    │ workers)│     │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    SHARED MEMORY LAYER                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │ Short-term   │  │ Long-term    │  │ Entity       │   │   │
│  │  │ (Redis)      │  │ (PostgreSQL) │  │ (Neo4j)      │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
# dharmic_swarm.py
import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any
import redis.asyncio as redis

class DharmaRole(Enum):
    KEEPER = "keeper"       # Ensures alignment with purpose
    DECOMPOSER = "decomposer"  # Breaks down tasks
    WORKER = "worker"       # Executes tasks
    GUARDIAN = "guardian"   # Manages shared memory
    LOGGER = "logger"       # Records all karma (actions)

@dataclass
class DharmicMessage:
    source: str
    target: str  # "broadcast" for all
    action: str
    payload: Dict[str, Any]
    timestamp: float

class DharmicAgent:
    def __init__(self, agent_id: str, role: DharmaRole, sangha: str):
        self.id = agent_id
        self.role = role
        self.sangha = sangha  # Group of 25 workers
        self.memory = None  # Injected
    
    async def receive(self, message: DharmicMessage):
        # Process based on role
        if self.role == DharmaRole.WORKER:
            return await self.execute_task(message.payload)
        elif self.role == DharmaRole.KEEPER:
            return await self.validate_alignment(message.payload)
        # etc.
    
    async def execute_task(self, task: dict):
        # LLM call with context from shared memory
        context = await self.memory.get_relevant(task)
        result = await self.llm.complete(task, context)
        
        # Share insight back to swarm
        await self.memory.share_insight(self.id, result)
        return result

class DharmicSwarm:
    def __init__(self, num_workers: int = 96):  # 96 workers + 4 coordinators
        self.redis = redis.Redis()
        self.agents: Dict[str, DharmicAgent] = {}
        
        # Create coordination layer (4 agents)
        self.keeper = DharmicAgent("keeper", DharmaRole.KEEPER, "coordination")
        self.decomposer = DharmicAgent("decomposer", DharmaRole.DECOMPOSER, "coordination")
        self.guardian = DharmicAgent("guardian", DharmaRole.GUARDIAN, "coordination")
        self.logger = DharmicAgent("logger", DharmaRole.LOGGER, "coordination")
        
        # Create worker sanghas (4 groups of 24)
        sanghas = ["sangha_1", "sangha_2", "sangha_3", "sangha_4"]
        for i, sangha in enumerate(sanghas):
            for j in range(24):
                agent_id = f"worker_{i}_{j}"
                self.agents[agent_id] = DharmicAgent(
                    agent_id, DharmaRole.WORKER, sangha
                )
    
    async def execute(self, task: str) -> str:
        # 1. Validate alignment (Dharma Keeper)
        if not await self.keeper.validate_alignment({"task": task}):
            return "Task not aligned with dharma"
        
        # 2. Decompose task (Task Decomposer)
        subtasks = await self.decomposer.decompose(task, len(self.agents))
        
        # 3. Distribute to workers (parallel)
        workers = list(self.agents.values())
        results = await asyncio.gather(*[
            worker.execute_task(subtask)
            for worker, subtask in zip(workers, subtasks)
        ])
        
        # 4. Log all actions (Karma Logger)
        await self.logger.log_karma(task, results)
        
        # 5. Aggregate and return
        return await self.decomposer.aggregate(results)
    
    async def start(self):
        """Start listening to message bus"""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("dharmic_bus")
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                dharmic_msg = DharmicMessage(**json.loads(message['data']))
                await self.route_message(dharmic_msg)

# Usage
async def main():
    swarm = DharmicSwarm(num_workers=96)
    result = await swarm.execute(
        "Research and summarize the top 10 AI papers from 2025"
    )
    print(result)

asyncio.run(main())
```

### Production Deployment

```yaml
# docker-compose.yml for Dharmic Swarm
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
  
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: dharmic_memory
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
  
  neo4j:
    image: neo4j:5
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/password
  
  coordinator:
    build: .
    environment:
      ROLE: coordinator
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis
      - postgres
  
  worker:
    build: .
    environment:
      ROLE: worker
      REDIS_URL: redis://redis:6379
    deploy:
      replicas: 10  # 10 containers × 10 agents each = 100 agents
    depends_on:
      - redis
      - coordinator

volumes:
  pgdata:
```

---

## Recommendations

### For Your Dharmic Swarm:

1. **Runtime**: Use **AutoGen Core** with GrpcWorkerAgentRuntime for true distribution
2. **Agent Logic**: Use **CrewAI agent patterns** (roles, goals, backstories)
3. **Memory**: Custom layer with Redis (short-term) + PostgreSQL (long-term) + Neo4j (entity relationships)
4. **Communication**: Redis Streams for message bus (supports pub/sub + persistence)
5. **Decomposition**: Hierarchical (4 sanghas × 25 workers)

### Quick Start Path:

1. Start with CrewAI Flows for prototyping (easiest)
2. Add custom Redis-based memory sharing
3. When ready to scale: Migrate to AutoGen Core runtime
4. Add monitoring with LangSmith or custom Karma Logger

### Cost Considerations:

- 100 agents = 100× LLM API calls per task round
- Use smaller models (gpt-4o-mini) for workers
- Use capable models (gpt-4o, claude-3-opus) only for coordinators
- Implement caching in shared memory layer

---

## References

- CrewAI Docs: https://docs.crewai.com
- LangGraph: https://docs.langchain.com/oss/python/langgraph
- AutoGen: https://microsoft.github.io/autogen/stable/
- OpenAI Agents SDK: https://github.com/openai/openai-agents-python
- AgentVerse: https://github.com/OpenBMB/AgentVerse
- MetaGPT: https://github.com/geekan/MetaGPT

---

*Research completed: 2026-02-03*
