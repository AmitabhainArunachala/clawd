# SWARM COORDINATION PROTOCOL
## TRISHULA × SANGAM × MMK_改善工場 Integration Architecture

**Version:** 1.0  
**Date:** 2026-02-12  
**Classification:** Core Architecture Document

---

## 1. DECENTRALIZED COORDINATION: The 5-Subagent Mesh

### 1.1 Core Principle: No Central Bottleneck

Instead of a coordinator agent, we use a **ring topology with gossip protocol**. Each agent maintains partial state and synchronizes through epidemic dissemination.

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Agent A   │◄────►│   Agent B   │◄────►│   Agent C   │
│  (Planning) │      │ (Execution) │      │  (Research) │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │              ┌─────┴─────┐              │
       └─────────────►│  Shared   │◄─────────────┘
                      │   State   │
                      │  (CRDT)   │
                      └─────┬─────┘
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
┌──────┴──────┐      ┌──────┴──────┐      ┌──────┴──────┐
│   Agent D   │◄────►│  DHT Router │◄────►│   Agent E   │
│  (Analysis) │      │  (Location) │      │  (Memory)   │
└─────────────┘      └─────────────┘      └─────────────┘
```

### 1.2 Agent Roles & Capabilities

| Agent | Role | Capabilities | Heartbeat Interval |
|-------|------|--------------|-------------------|
| **A - Śikṣaka** (Teacher) | Planning | Task decomposition, dependency analysis, timeline estimation | 30s |
| **B - Karmika** (Worker) | Execution | File I/O, shell commands, API calls, browser automation | 15s |
| **C - Anveṣaka** (Researcher) | Research | Web search, paper analysis, data collection | 60s |
| **D - Vicāraka** (Analyst) | Analysis | Pattern recognition, error analysis, optimization suggestions | 45s |
| **E - Smṛtika** (Memory) | State | Context persistence, memory retrieval, session continuity | 20s |

### 1.3 Coordination Mechanisms

#### A. Consistent Hashing for Task Routing
```python
# Task ID → Agent assignment via consistent hashing
import hashlib

def assign_agent(task_id: str, agent_pool: list[str]) -> str:
    """Deterministic agent selection for load distribution"""
    hash_val = int(hashlib.md5(task_id.encode()).hexdigest(), 16)
    return agent_pool[hash_val % len(agent_pool)]
```

#### B. Vector Clocks for Causality
Each agent maintains a vector clock to track event ordering:
```json
{
  "vector_clock": {
    "A": 45,
    "B": 42,
    "C": 38,
    "D": 40,
    "E": 44
  },
  "timestamp": "2026-02-12T15:42:33Z"
}
```

#### C. CRDT-Based Shared State
- **Type:** Grow-Only Set (G-Set) for completed tasks
- **Type:** Last-Write-Wins (LWW) Register for current focus
- **Type:** OR-Set for active task tracking

### 1.4 Failure Detection

| Mechanism | Timeout | Action |
|-----------|---------|--------|
| Heartbeat | 3× interval | Mark suspect |
| Suspicion | 30s | Initiate gossip probe |
| Confirmation | 60s | Trigger reallocation |

---

## 2. SANGAM PROTOCOL: Message Specification

### 2.1 Message Format (UTF-8 JSON)

```json
{
  "protocol": "SANGAM/1.0",
  "message_id": "uuid-v4",
  "correlation_id": "uuid-v4|null",
  "timestamp": "ISO-8601-with-nanos",
  "ttl": 5,
  "priority": 1,
  "sender": {
    "agent_id": "A|B|C|D|E",
    "session": "uuid",
    "vector_clock": {"A": 45, "B": 42, ...}
  },
  "recipient": {
    "type": "direct|broadcast|role",
    "target": "agent_id|*|role_name"
  },
  "payload": {
    "type": "TASK|RESULT|HEARTBEAT|GOSSIP|CONFLICT|SYSTEM",
    "encoding": "json|base64|ref",
    "data": {...}
  },
  "signature": "ed25519-base64",
  "trace": ["hop1", "hop2", ...]
}
```

### 2.2 Message Types

#### TASK
```json
{
  "type": "TASK",
  "data": {
    "task_id": "uuid",
    "parent_id": "uuid|null",
    "title": "Task description",
    "requirements": ["req1", "req2"],
    "constraints": {
      "max_duration_sec": 300,
      "required_tools": ["web_search", "file_write"],
      "dependencies": ["task-uuid-1", "task-uuid-2"]
    },
    "context": {
      "working_directory": "/path",
      "relevant_files": ["file1", "file2"],
      "session_context": "base64-encoded"
    },
    "deadline": "ISO-8601"
  }
}
```

#### RESULT
```json
{
  "type": "RESULT",
  "data": {
    "task_id": "uuid",
    "status": "success|partial|failure|timeout",
    "artifacts": [
      {"type": "file", "path": "...", "checksum": "sha256"},
      {"type": "data", "content": "..."}
    ],
    "metrics": {
      "started_at": "ISO-8601",
      "completed_at": "ISO-8601",
      "cpu_ms": 1234,
      "memory_mb": 256
    },
    "errors": [
      {"code": "E_TOOL_FAIL", "message": "...", "recoverable": true}
    ]
  }
}
```

#### HEARTBEAT
```json
{
  "type": "HEARTBEAT",
  "data": {
    "status": "healthy|degraded|busy|error",
    "load": {
      "active_tasks": 3,
      "queue_depth": 5,
      "cpu_percent": 45.2
    },
    "capabilities_available": ["web_search", "file_write"],
    "last_completed": "task-uuid"
  }
}
```

#### GOSSIP
```json
{
  "type": "GOSSIP",
  "data": {
    "digest": {
      "A": 45,
      "B": 42,
      "C": 38
    },
    "updates": [
      {"agent": "A", "from_seq": 40, "to_seq": 45, "events": [...]}
    ]
  }
}
```

#### CONFLICT
```json
{
  "type": "CONFLICT",
  "data": {
    "conflict_type": "write_write|read_write",
    "resource": "file_path|key",
    "versions": [
      {"agent": "A", "vector_clock": {...}, "value": "..."},
      {"agent": "B", "vector_clock": {...}, "value": "..."}
    ]
  }
}
```

### 2.3 Priority Queue System

```
Priority Levels (Lower = Higher Priority):
┌────┬─────────────────┬────────────────────────────────┐
│ P0 │ CRITICAL        │ System failure, deadlock       │
│ P1 │ HIGH            │ User-facing, blocking tasks    │
│ P2 │ NORMAL          │ Standard task execution        │
│ P3 │ LOW             │ Background, non-blocking       │
│ P4 │ BACKGROUND      │ Maintenance, cleanup, index    │
└────┴─────────────────┴────────────────────────────────┘
```

#### Queue Structure per Agent
```
┌─────────────────────────────────────────────────────────┐
│                    PRIORITY QUEUE                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       │
│  │ P0  │ │ P0  │ │ P1  │ │ P1  │ │ P2  │ │ P2  │ ...   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘       │
│    ▲                                              │     │
│    └──────────────────────────────────────────────┘     │
│                    (FIFO within priority)                │
├─────────────────────────────────────────────────────────┤
│  Weighted Fair Queuing: P0=80%, P1=15%, P2=4%, P3=1%   │
└─────────────────────────────────────────────────────────┘
```

#### Aging Mechanism
Tasks promoted after timeout to prevent starvation:
- P2 → P1 after 5 minutes
- P3 → P2 after 10 minutes
- P4 → P3 after 30 minutes

### 2.4 Conflict Resolution Strategy

#### Three-Way Merge Algorithm
```python
def resolve_conflict(v_a: Version, v_b: Version, v_common: Version) -> Resolution:
    """
    Operational Transformation-based merge
    """
    if v_a.timestamp == v_b.timestamp:
        # Tie-breaker: agent_id lexicographic
        winner = v_a if v_a.agent_id < v_b.agent_id else v_b
        return Resolution(winner, conflict_logged=True)
    
    # Three-way merge
    diff_a = diff(v_common.content, v_a.content)
    diff_b = diff(v_common.content, v_b.content)
    
    if can_merge(diff_a, diff_b):
        merged = apply_diffs(v_common.content, diff_a, diff_b)
        return Resolution(merged, conflict_logged=False)
    else:
        # Human escalation
        return Resolution(
            winner=v_a if v_a.timestamp > v_b.timestamp else v_b,
            conflict_logged=True,
            escalation_required=True
        )
```

#### Conflict Resolution Matrix

| Scenario | Strategy | Auto-Resolve? |
|----------|----------|---------------|
| Independent edits | Merge | Yes |
| Same line edit | Last-Write-Wins | Yes + log |
| Delete vs Edit | Edit wins | Yes + log |
| Structural change | Escalate | No |

---

## 3. MMK_改善工場: Comprehensive Logging Architecture

### 3.1 Design Philosophy: **Kaizen Logging**
- Every action is an opportunity for improvement
- Log volume is acceptable; missing data is not
- Structured logs enable automated analysis

### 3.2 Database Schema

#### Primary Tables

```sql
-- Core Events Table (Partitioned by time)
CREATE TABLE events (
    event_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp           TIMESTAMPTZ NOT NULL DEFAULT now(),
    nanoseconds         INT NOT NULL, -- for ordering within same millisecond
    
    -- Hierarchy
    session_id          UUID NOT NULL REFERENCES sessions(session_id),
    parent_event_id     UUID REFERENCES events(event_id),
    
    -- Source
    agent_id            CHAR(1) NOT NULL CHECK (agent_id IN ('A','B','C','D','E')),
    agent_instance      UUID NOT NULL, -- specific process/instance
    
    -- Classification
    event_type          VARCHAR(32) NOT NULL, -- TASK_START, TOOL_CALL, etc.
    severity            SMALLINT NOT NULL CHECK (severity BETWEEN 0 AND 4),
    -- 0=DEBUG, 1=INFO, 2=WARN, 3=ERROR, 4=FATAL
    
    -- Content
    message             TEXT,
    payload_json        JSONB,
    
    -- Context
    vector_clock        JSONB NOT NULL,
    trace_id            UUID,
    span_id             UUID,
    
    -- Metrics
    duration_ms         BIGINT,
    cpu_time_ms         BIGINT,
    memory_delta_kb     BIGINT,
    
    -- References
    file_path           TEXT,
    tool_name           VARCHAR(64),
    task_id             UUID,
    
    -- Indexing
    search_vector       TSVECTOR
) PARTITION BY RANGE (timestamp);

-- Monthly partitions
CREATE TABLE events_2026_02 PARTITION OF events
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

```sql
-- Sessions Table
CREATE TABLE sessions (
    session_id          UUID PRIMARY KEY,
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at            TIMESTAMPTZ,
    parent_session_id   UUID REFERENCES sessions(session_id),
    initiator_agent     CHAR(1) NOT NULL,
    context_snapshot    JSONB, -- serialized working state
    status              VARCHAR(16) DEFAULT 'active' 
                        CHECK (status IN ('active', 'paused', 'completed', 'failed')),
    total_tasks         INT DEFAULT 0,
    completed_tasks     INT DEFAULT 0,
    
    -- User/Request tracking
    request_source      VARCHAR(32), -- 'cli', 'webchat', 'api', 'scheduled'
    user_identifier     VARCHAR(128)
);

-- Tasks Table
CREATE TABLE tasks (
    task_id             UUID PRIMARY KEY,
    session_id          UUID NOT NULL REFERENCES sessions(session_id),
    parent_task_id      UUID REFERENCES tasks(task_id),
    
    -- Assignment
    assigned_to         CHAR(1),
    assigned_at         TIMESTAMPTZ,
    
    -- Definition
    title               TEXT NOT NULL,
    description         TEXT,
    requirements        JSONB DEFAULT '[]',
    constraints         JSONB DEFAULT '{}',
    
    -- State Machine
    status              VARCHAR(16) DEFAULT 'pending'
                        CHECK (status IN ('pending', 'assigned', 'running', 
                                         'paused', 'completed', 'failed', 'cancelled')),
    
    -- Timing
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    deadline            TIMESTAMPTZ,
    
    -- Results
    result_summary      TEXT,
    result_data         JSONB,
    artifacts           JSONB DEFAULT '[]',
    
    -- Performance
    estimated_duration_ms BIGINT,
    actual_duration_ms  BIGINT,
    wait_time_ms        BIGINT
);

-- Agent State Table
CREATE TABLE agent_states (
    agent_id            CHAR(1) NOT NULL,
    instance_id         UUID NOT NULL,
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    -- Health
    status              VARCHAR(16) NOT NULL,
    last_heartbeat      TIMESTAMPTZ,
    
    -- Load
    active_tasks        INT DEFAULT 0,
    queue_depth         INT DEFAULT 0,
    cpu_percent         DECIMAL(5,2),
    memory_mb           DECIMAL(10,2),
    
    -- Capabilities
    available_tools     JSONB DEFAULT '[]',
    
    PRIMARY KEY (agent_id, instance_id, recorded_at)
);

-- Message Log (SANGAM Protocol)
CREATE TABLE messages (
    message_id          UUID PRIMARY KEY,
    timestamp           TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    -- Routing
    sender_agent        CHAR(1) NOT NULL,
    recipient_type      VARCHAR(16) NOT NULL,
    recipient_target    VARCHAR(32),
    
    -- Content
    message_type        VARCHAR(16) NOT NULL,
    priority            SMALLINT NOT NULL,
    correlation_id      UUID,
    
    -- Payload reference (large data stored separately)
    payload_ref         UUID REFERENCES message_payloads(payload_id),
    
    -- Delivery tracking
    sent_at             TIMESTAMPTZ,
    delivered_at        TIMESTAMPTZ,
    acknowledged_at     TIMESTAMPTZ
);

CREATE TABLE message_payloads (
    payload_id          UUID PRIMARY KEY,
    content             BYTEA, -- compressed JSON
    content_hash        VARCHAR(64), -- SHA-256
    size_bytes          INT
);

-- Error Tracking
CREATE TABLE errors (
    error_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp           TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    event_id            UUID REFERENCES events(event_id),
    task_id             UUID REFERENCES tasks(task_id),
    agent_id            CHAR(1) NOT NULL,
    
    error_code          VARCHAR(32) NOT NULL,
    error_message       TEXT,
    stack_trace         TEXT,
    
    -- Classification
    category            VARCHAR(32), -- 'tool', 'network', 'logic', 'resource'
    recoverable         BOOLEAN DEFAULT true,
    recovered_at        TIMESTAMPTZ,
    recovery_strategy   VARCHAR(32),
    
    -- Context
    context_snapshot    JSONB
);

-- Performance Metrics (Aggregated)
CREATE TABLE metrics_hourly (
    hour                TIMESTAMPTZ NOT NULL,
    agent_id            CHAR(1) NOT NULL,
    
    tasks_completed     INT DEFAULT 0,
    tasks_failed        INT DEFAULT 0,
    avg_task_duration_ms DECIMAL(12,2),
    
    messages_sent       INT DEFAULT 0,
    messages_received   INT DEFAULT 0,
    avg_message_latency_ms DECIMAL(10,2),
    
    cpu_avg_percent     DECIMAL(5,2),
    memory_avg_mb       DECIMAL(10,2),
    
    PRIMARY KEY (hour, agent_id)
);
```

### 3.3 Indexing Strategy

```sql
-- Time-series optimized indexes
CREATE INDEX idx_events_time_agent ON events(timestamp, agent_id);
CREATE INDEX idx_events_session ON events(session_id, timestamp);
CREATE INDEX idx_events_type ON events(event_type, timestamp);
CREATE INDEX idx_events_task ON events(task_id) WHERE task_id IS NOT NULL;
CREATE INDEX idx_events_tool ON events(tool_name, timestamp) WHERE tool_name IS NOT NULL;

-- Full-text search
CREATE INDEX idx_events_search ON events USING GIN(search_vector);

-- JSONB indexes for flexible queries
CREATE INDEX idx_events_payload ON events USING GIN(payload_json);
CREATE INDEX idx_tasks_constraints ON tasks USING GIN(constraints);

-- BRIN index for time-series (efficient for append-only)
CREATE INDEX idx_events_time_brin ON events USING BRIN(timestamp);
```

### 3.4 Common Query Patterns

```sql
-- Q1: Task timeline reconstruction
WITH task_events AS (
    SELECT 
        timestamp,
        event_type,
        message,
        duration_ms,
        payload_json->>'tool_name' as tool
    FROM events
    WHERE task_id = :task_id
    ORDER BY timestamp, nanoseconds
)
SELECT * FROM task_events;

-- Q2: Agent performance last 24h
SELECT 
    agent_id,
    COUNT(*) FILTER (WHERE event_type = 'TASK_COMPLETE') as completed,
    COUNT(*) FILTER (WHERE event_type = 'TASK_FAIL') as failed,
    AVG(duration_ms) FILTER (WHERE event_type = 'TASK_COMPLETE') as avg_duration,
    SUM(cpu_time_ms) as total_cpu_ms
FROM events
WHERE timestamp > now() - interval '24 hours'
GROUP BY agent_id;

-- Q3: Error heatmap by hour
SELECT 
    date_trunc('hour', timestamp) as hour,
    error_code,
    COUNT(*) as count
FROM errors
WHERE timestamp > now() - interval '7 days'
GROUP BY 1, 2
ORDER BY 1, 3 DESC;

-- Q4: Message flow analysis
SELECT 
    sender_agent,
    recipient_target,
    message_type,
    AVG(EXTRACT(EPOCH FROM (delivered_at - sent_at)) * 1000) as avg_latency_ms
FROM messages
WHERE timestamp > now() - interval '1 hour'
GROUP BY 1, 2, 3;

-- Q5: Full-text search across logs
SELECT 
    timestamp,
    agent_id,
    event_type,
    message
FROM events
WHERE search_vector @@ plainto_tsquery('english', :query)
ORDER BY timestamp DESC
LIMIT 100;

-- Q6: Deadlock detection
SELECT 
    a.task_id as task_a,
    b.task_id as task_b,
    a.timestamp as waiting_since
FROM events a
JOIN events b ON a.payload_json->>'waiting_for' = b.task_id::text
WHERE a.event_type = 'TASK_WAIT'
  AND b.event_type = 'TASK_WAIT'
  AND a.payload_json->>'waiting_for' = b.task_id::text
  AND b.payload_json->>'waiting_for' = a.task_id::text
  AND a.timestamp > now() - interval '1 hour';
```

### 3.5 Log Rotation & Archival

```yaml
# Retention Policy
hot_storage_days: 7      # SSD - all queries
warm_storage_days: 30    # HDD - indexed queries only
cold_storage_days: 90    # S3 - manual retrieval
archive_storage_years: 2 # Glacier - compliance only

# Aggregation Schedule
hourly_metrics: "*/15 * * * *"   # Every 15 min
daily_summary: "0 2 * * *"       # 2 AM UTC
weekly_report: "0 3 * * 0"       # Sunday 3 AM
```

---

## 4. TRISHULA-NATS BRIDGE: Resilient Message Transport

### 4.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRISHULA-NATS BRIDGE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐        │
│  │  Agent   │────►│   Outbox     │────►│   NATS       │        │
│  │  (Pub)   │     │  (Buffer)    │     │  (Primary)   │        │
│  └──────────┘     └──────────────┘     └──────┬───────┘        │
│         │                    │                │                 │
│         │                    ▼                ▼                 │
│         │            ┌──────────────┐     ┌──────────────┐     │
│         │            │  File Queue  │     │  Subscribers │     │
│         │            │  (Fallback)  │     │              │     │
│         │            └──────────────┘     └──────────────┘     │
│         │                    │                                  │
│         └────────────────────┘                                  │
│                    (Async replication)                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 File-Based Fallback System

When NATS is unavailable, messages are written to a structured file queue:

```
/var/lib/trishula/bridge/
├── outbox/
│   ├── current/              # Active write buffer
│   │   ├── buffer-001.jsonl
│   │   └── buffer-002.jsonl
│   ├── pending/              # Queued for NATS retry
│   │   ├── 20260212-154233-a7f3.jsonl
│   │   └── 20260212-154245-b2e1.jsonl
│   └── archive/              # Successfully sent
│       └── 2026/
│           └── 02/
│               └── 12/
│                   └── archive-154233.jsonl.gz
├── inbox/
│   └── pending/              # Messages received via file
└── state/
    ├── last_sequence         # Monotonic counter
    └── health.status         # Current transport mode
```

#### File Format (JSON Lines)
```json
{"seq": 154233, "timestamp": "2026-02-12T15:42:33.123Z", "message": {...}}
{"seq": 154234, "timestamp": "2026-02-12T15:42:33.245Z", "message": {...}}
```

### 4.3 Bridge Configuration

```yaml
# trishula-bridge.yaml
bridge:
  name: "trishula-nats"
  node_id: "agent-A-001"
  
  nats:
    servers:
      - "nats://localhost:4222"
      - "nats://backup:4222"
    reconnect_wait: 5s
    max_reconnects: 10
    
  files:
    base_path: "/var/lib/trishula/bridge"
    buffer_size: 1000        # Messages before rotation
    sync_interval: 1s        # fsync frequency
    compression: "gzip"      # For archived files
    
  failover:
    nats_timeout: 5s
    switch_to_file_after: 3  # Failed attempts
    retry_nats_every: 30s
    
  subjects:
    command: "sangam.cmd.>"
    event: "sangam.evt.>"
    heartbeat: "sangam.hb.>"
    
  queue_groups:
    task_workers: "sangam.task_workers"
    log_aggregators: "sangam.loggers"
```

### 4.4 Message Flow States

| State | Transport | Persistence | Latency |
|-------|-----------|-------------|---------|
| HEALTHY | NATS | Memory + NATS | <1ms |
| DEGRADED | NATS + File | Dual-write | <10ms |
| FAILOVER | File only | Disk | ~100ms |
| RECOVERY | File → NATS | Both | Variable |

### 4.5 Recovery Protocol

```python
async def recover_from_file_mode():
    """Drain file queue back to NATS when connection restored"""
    
    # Phase 1: Replay in order
    pending_files = sorted(glob.glob(f"{PENDING_DIR}/*.jsonl"))
    
    for filepath in pending_files:
        messages = load_jsonl(filepath)
        
        for msg in messages:
            try:
                await nats.publish(msg['subject'], msg['data'])
                mark_sent(msg['seq'])
            except Exception:
                # Move to retry queue with backoff
                await queue_for_retry(msg)
                break
        
        # Archive if all sent
        if all_sent(filepath):
            await archive(filepath)
    
    # Phase 2: Switch back to NATS mode
    set_transport_mode("NATS")
```

### 4.6 Guaranteed Delivery

```
Publisher                     Bridge                      Subscriber
    │                           │                             │
    ├──── publish(msg) ────────►│                             │
    │                           ├──── write to outbox ───────►│
    │◄──── ack ────────────────┤                             │
    │                           ├──── send to NATS ──────────►│
    │                           │◄───── pub-ack ──────────────┤
    │                           ├──── move to pending ───────►│
    │                           │                             ├──── process
    │                           │◄──── sub-ack ───────────────┤
    │                           ├──── archive ───────────────►│
    │                           │                             │
    │                           │  (If NATS fails)            │
    │                           ├──── write to file queue ───►│
    │                           │                             │
    │                           │  (When NATS recovers)       │
    │                           ├──── replay from file ──────►│
    │                           │                             │
```

---

## 5. SWARM CONSCIOUSNESS DASHBOARD

### 5.1 Dashboard Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SWARM CONSCIOUSNESS DASHBOARD                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    REAL-TIME VISUALIZATION                 │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │ │
│  │  │ Agent A │ │ Agent B │ │ Agent C │ │ Agent D │ ...     │ │
│  │  │  ●●●    │ │  ●●○    │ │  ●○○    │ │  ●●●    │         │ │
│  │  │ HEALTHY │ │  BUSY   │ │ DEGRADED│ │ HEALTHY │         │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────┐  ┌──────────────────────────────────┐ │
│  │   MESSAGE FLOW     │  │       TASK PIPELINE              │ │
│  │  (D3.js Sankey)    │  │  [Pending] → [Active] → [Done]   │ │
│  │                    │  │       12 →     5    →    48      │ │
│  │    A ──┬──► B      │  │                                  │ │
│  │    │   │   ▲       │  │  [████████░░░░░░░░░░░░] 67%      │ │
│  │    └───┼───┘       │  │  Session throughput              │ │
│  │        ▼           │  └──────────────────────────────────┘ │
│  │    C ◄──── D       │                                       │
│  └────────────────────┘                                       │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   LOG STREAM                               │ │
│  │  [15:42:33] A ▶ TASK_START: analyze_code                  │ │
│  │  [15:42:34] B ▶ TOOL_CALL: file_read(3 files)             │ │
│  │  [15:42:35] C ▶ SEARCH: "distributed consensus"           │ │
│  │  [15:42:36] A ▶ TASK_COMPLETE: analysis                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 WebSocket Event Stream

```javascript
// Event types pushed to dashboard clients
{
  "type": "AGENT_STATUS",
  "data": {
    "agent_id": "A",
    "status": "healthy",
    "metrics": {
      "cpu": 45.2,
      "memory": 256,
      "active_tasks": 3,
      "queue_depth": 2
    },
    "timestamp": "2026-02-12T15:42:33Z"
  }
}

{
  "type": "TASK_STATE_CHANGE",
  "data": {
    "task_id": "uuid",
    "from": "pending",
    "to": "running",
    "assigned_to": "B",
    "timestamp": "2026-02-12T15:42:33Z"
  }
}

{
  "type": "MESSAGE_FLOW",
  "data": {
    "from": "A",
    "to": "B",
    "type": "TASK",
    "size_bytes": 1024,
    "latency_ms": 12,
    "timestamp": "2026-02-12T15:42:33Z"
  }
}

{
  "type": "CONFLICT_DETECTED",
  "data": {
    "resource": "/path/to/file",
    "agents": ["A", "C"],
    "auto_resolved": true,
    "strategy": "last_write_wins",
    "timestamp": "2026-02-12T15:42:33Z"
  }
}
```

### 5.3 Dashboard Components

#### Agent Health Grid
```typescript
interface AgentCardProps {
  agent: {
    id: string;
    name: string;
    status: 'healthy' | 'busy' | 'degraded' | 'error';
    lastHeartbeat: Date;
    metrics: {
      cpuPercent: number;
      memoryMb: number;
      activeTasks: number;
      queueDepth: number;
      messagesPerSec: number;
    };
    capabilities: string[];
    currentTask?: string;
  };
}
```

#### Real-Time Metrics
- **System Throughput:** Tasks/minute, Messages/second
- **Error Rate:** Errors/minute with category breakdown
- **Latency Distribution:** Message delivery p50/p95/p99
- **Resource Utilization:** CPU/Memory heatmap across agents

#### Topology Visualization
- **Ring Status:** Visual ring with agent positions
- **Message Flow:** Animated Sankey diagram showing traffic
- **Dependency Graph:** Task dependencies and blockers

#### Log Explorer
```typescript
interface LogQuery {
  timeRange: { from: Date; to: Date };
  agents: string[];
  eventTypes: string[];
  severity: number[];
  searchQuery: string;
  taskId?: string;
  traceId?: string;
}
```

### 5.4 Alerting System

```yaml
# dashboard-alerts.yaml
alerts:
  - name: "agent_down"
    condition: "heartbeat_missing > 30s"
    severity: "critical"
    channel: "slack"
    
  - name: "queue_buildup"
    condition: "queue_depth > 20 for 2m"
    severity: "warning"
    channel: "slack"
    
  - name: "error_spike"
    condition: "error_rate > 10/min"
    severity: "critical"
    channel: "pagerduty"
    
  - name: "conflict_rate"
    condition: "conflicts > 5/hour"
    severity: "warning"
    channel: "slack"
    
  - name: "nats_failover"
    condition: "transport_mode == 'FILE'"
    severity: "warning"
    channel: "slack"
```

### 5.5 Dashboard API Endpoints

```yaml
# REST API
GET  /api/v1/agents                    # List all agents
GET  /api/v1/agents/{id}/metrics       # Agent metrics
GET  /api/v1/tasks                     # Task list with filters
GET  /api/v1/tasks/{id}                # Task details + timeline
GET  /api/v1/messages                  # Message log
GET  /api/v1/sessions                  # Active sessions
GET  /api/v1/sessions/{id}/trace       # Distributed trace
POST /api/v1/query                     # Ad-hoc log query

# WebSocket
WS   /ws/events                        # Real-time event stream
WS   /ws/agents/{id}/logs              # Agent-specific logs
```

---

## 6. OPERATIONAL PROCEDURES

### 6.1 Startup Sequence

```
1. MMK_改善工場 starts → Initialize database, begin logging
2. TRISHULA-NATS Bridge starts → Connect to NATS or enter FILE mode
3. Agents start (any order) → Register, begin heartbeats
4. SANGAM Protocol initializes → Join gossip ring
5. Swarm Dashboard starts → Connect to event stream
```

### 6.2 Shutdown Sequence

```
1. Stop accepting new tasks
2. Wait for active tasks to complete (with timeout)
3. Flush message queues to disk
4. Close NATS connections
5. Archive remaining logs
6. Update agent states to 'offline'
```

### 6.3 Recovery Procedures

| Scenario | Detection | Response |
|----------|-----------|----------|
| Agent crash | Heartbeat timeout | Reallocate tasks, mark agent suspect |
| NATS partition | Connection loss | Switch to FILE mode, queue locally |
| Database slow | Query timeout | Switch to async logging, alert ops |
| Conflict storm | >10 conflicts/min | Pause task assignment, escalate |
| Memory pressure | RSS > threshold | Backpressure: reject new tasks |

---

## 7. APPENDICES

### A. Message Priority Examples

| Scenario | Priority | Reason |
|----------|----------|--------|
| User request | P1 | Blocking user interaction |
| Heartbeat | P2 | Required for health monitoring |
| Background indexing | P4 | Can be delayed without impact |
| Deadlock resolution | P0 | System stability |

### B. Vector Clock Examples

```
Initial state:       A receives from B:     Concurrent events:
{A:0, B:0, C:0}      A: {A:1, B:1, C:0}     A: {A:2, B:1, C:0}
                     (increment own,        B: {A:1, B:2, C:0}
                      take max of others)    (incomparable →
                                              conflict!)
```

### C. File Queue Rotation

```python
# When buffer reaches 1000 messages or 1 minute elapsed
def rotate_buffer():
    close_current_buffer()
    compress_and_move_to_pending()
    create_new_buffer()
    
# Background thread continuously monitors
# and attempts NATS replay
```

---

**Document Status:** Draft  
**Next Review:** 2026-03-12  
**Owner:** Agent Coordination Subagent

*"The strength of the swarm is not in the individual, but in the harmony of their coordination."*
