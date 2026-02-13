# Digital Mahashakti - Coordination Architecture
## TRISHULA / SANGAM / MMKT Integration Design

Document Version: 1.0
Date: 2026-02-12
Author: Coordination Subagent

================================================================================
TABLE OF CONTENTS
================================================================================

1. SANGAM Message Protocol
2. TRISHULA-NATS Bridge
3. MMKT Logging Schema
4. Swarm Dashboard Architecture
5. Conflict Resolution System
6. File Sync Protocol (AGNI-RUSHABDEV-DC)

================================================================================
1. SANGAM MESSAGE PROTOCOL
================================================================================

SANGAM is the inter-agent communication protocol enabling message exchange
between autonomous agents in the Digital Mahashakti ecosystem.

------------------------------------------------------------------------------
1.1 MESSAGE STRUCTURE
------------------------------------------------------------------------------

Every SANGAM message follows a standardized envelope format:

```
SANGAM_MESSAGE
  message_id      : UUID v4 (unique per message)
  timestamp       : ISO-8601 UTC with milliseconds
  sender_id       : Agent identifier (e.g., "AGNI", "RUSHABDEV")
  recipient_id    : Target agent or "BROADCAST"
  message_type    : Type classification (see 1.2)
  priority        : CRITICAL / HIGH / NORMAL / LOW
  correlation_id  : UUID for request-response pairing
  payload         : Type-specific data (JSON)
  signature       : HMAC-SHA256(sender_key, message_body)
```

------------------------------------------------------------------------------
1.2 MESSAGE TYPES
------------------------------------------------------------------------------

COMMAND         - Directive requiring action from recipient
  Fields: action, parameters, deadline, timeout_seconds

QUERY           - Request for information
  Fields: query_type, query_params, max_results

RESPONSE        - Reply to QUERY or COMMAND acknowledgment
  Fields: in_reply_to, status (SUCCESS/FAILURE/PENDING), data, error_code

EVENT           - Fire-and-forget notification
  Fields: event_type, event_data, severity

HEARTBEAT       - Health status ping
  Fields: agent_status, load_metrics, memory_usage, uptime_seconds

CONFLICT        - Disagreement declaration
  Fields: conflicting_agents, subject, proposed_resolutions

------------------------------------------------------------------------------
1.3 ROUTING PATTERNS
------------------------------------------------------------------------------

POINT TO POINT
  Direct addressing: sender -> specific recipient_id
  
PUBLISH SUBSCRIBE
  Topic-based: agents subscribe to relevant channels
  Topics:
    - swarm.system.heartbeat
    - swarm.task.assigned
    - swarm.conflict.declared
    - swarm.file.changed
    - swarm.knowledge.new

REQUEST REPLY
  Correlation tracking via correlation_id
  Default timeout: 30 seconds
  Retry policy: 3 attempts with exponential backoff

------------------------------------------------------------------------------
1.4 MESSAGE FLOW DIAGRAM
------------------------------------------------------------------------------

  AGNI                    SANGAM BUS                 RUSHABDEV
    |                          |                          |
    |----COMMAND:analyze----->|                          |
    |                          |------COMMAND:analyze---->|
    |                          |                          |
    |                          |<-----RESPONSE:ack--------|
    |<----RESPONSE:ack--------|                          |
    |                          |                          |
    |                          |<----EVENT:progress------|
    |<---EVENT:progress-------|                          |
    |                          |                          |

================================================================================
2. TRISHULA-NATS BRIDGE
================================================================================

TRISHULA provides the three-pronged coordination layer:
- Discovery: Agent presence and capability registry
- Routing: Intelligent message delivery
- Enforcement: Policy compliance and rate limiting

------------------------------------------------------------------------------
2.1 BRIDGE ARCHITECTURE
------------------------------------------------------------------------------

TRISHULA implements a bridge between SANGAM protocol and NATS messaging
infrastructure for high-throughput, low-latency coordination.

```
+------------------+      +------------------+      +------------------+
|   SANGAM Agent   |      |   TRISHULA       |      |   NATS Server    |
|                  |<---->|   BRIDGE         |<---->|   Cluster        |
|  (AGNI, etc.)    |      |                  |      |                  |
+------------------+      +------------------+      +------------------+
          |                       |                         |
          | SANGAM MSG            | NATS Protocol           | JetStream
          |                       |                         |
```

------------------------------------------------------------------------------
2.2 COMPONENT RESPONSIBILITIES
------------------------------------------------------------------------------

TRIDENT_1 - DISCOVERY
  - Maintain registry of active agents
  - Broadcast agent join/leave events
  - Track agent capabilities and load
  - Provide service discovery API

TRIDENT_2 - ROUTING
  - Convert SANGAM messages to NATS subjects
  - Handle subject wildcard mapping
  - Implement message priority queues
  - Route based on agent availability

TRIDENT_3 - ENFORCEMENT
  - Validate message signatures
  - Enforce rate limits per agent
  - Apply message size restrictions
  - Log all cross-agent communication

------------------------------------------------------------------------------
2.3 NATS SUBJECT MAPPING
------------------------------------------------------------------------------

SANGAM message_type maps to NATS subject hierarchy:

  sangam.command.<sender>.<recipient>
  sangam.query.<sender>.<recipient>
  sangam.response.<recipient>.<sender>
  sangam.event.<event_type>.<sender>
  sangam.heartbeat.<agent_id>
  sangam.conflict.<conflict_id>

Wildcards:
  sangam.command.*.RUSHABDEV  - All commands TO RUSHABDEV
  sangam.event.task.*         - All task-related events
  sangam.heartbeat.>          - All heartbeat messages

------------------------------------------------------------------------------
2.4 JETSTREAM PERSISTENCE
------------------------------------------------------------------------------

Stream: SANGAM_MESSAGES
  Subjects: sangam.>
  Retention: WorkQueue (auto-delete after processing)
  MaxMsgs: 100000
  MaxAge: 24h
  Replication: 3 (clustered mode)

Stream: SANGAM_EVENTS
  Subjects: sangam.event.>
  Retention: Limits
  MaxMsgs: 500000
  MaxAge: 7d
  Replication: 3

Consumer: durable_agents
  Durable name: agent_pool
  Ack policy: Explicit
  Max deliver: 3
  Ack wait: 30s

================================================================================
3. MMKT LOGGING SCHEMA
================================================================================

MMKT (Mahashakti Kaizen Tracking) provides structured logging for
continuous improvement and operational visibility.

------------------------------------------------------------------------------
3.1 LOG LEVELS
------------------------------------------------------------------------------

DEBUG     - Detailed diagnostic information
INFO      - General operational events
NOTICE    - Significant but normal events
WARNING   - Anomalous but handled conditions
ERROR     - Failed operations requiring attention
CRITICAL  - System-threatening failures

------------------------------------------------------------------------------
3.2 CORE SCHEMA FIELDS
------------------------------------------------------------------------------

Every MMKT log entry contains:

  timestamp        : ISO-8601 with microseconds precision
  level            : Log level from 3.1
  agent_id         : Originating agent identifier
  session_id       : Unique session correlation ID
  trace_id         : Distributed trace identifier
  span_id          : Current span within trace
  parent_span_id   : Parent span reference
  message          : Human-readable log message
  context          : Structured key-value data

------------------------------------------------------------------------------
3.3 EVENT CATEGORIES
------------------------------------------------------------------------------

SYSTEM
  Fields: boot_time, memory_mb, cpu_percent, disk_free_gb
  
AGENT_TASK
  Fields: task_id, task_type, input_size, output_size, 
          duration_ms, status, error_details

COORDINATION
  Fields: message_id, peer_agent, protocol, latency_ms,
          retry_count, failure_reason

FILE_OPERATION
  Fields: operation (read/write/sync), path, size_bytes,
          checksum, source_agent, dest_agent

CONFLICT
  Fields: conflict_id, resolution_strategy, voting_outcome,
          resolved_by, resolution_time_ms

LEARNING
  Fields: improvement_type, before_metric, after_metric,
          confidence_score, applied_at

------------------------------------------------------------------------------
3.4 OUTPUT DESTINATIONS
------------------------------------------------------------------------------

PRIMARY     : Local rotating files (JSON Lines format)
              /var/log/mmkt/agent_<id>_<date>.log
              
SECONDARY   : NATS stream for real-time aggregation
              Subject: mmkt.logs.<agent_id>.<level>
              
TERTIARY    : SQLite for queryable structured data
              Table: events (indexed by timestamp, level, category)

------------------------------------------------------------------------------
3.5 SAMPLE LOG ENTRY
------------------------------------------------------------------------------

{
  "timestamp": "2026-02-12T15:30:45.123456Z",
  "level": "INFO",
  "agent_id": "AGNI",
  "session_id": "sess_a1b2c3d4",
  "trace_id": "trace_987654321",
  "span_id": "span_0001",
  "parent_span_id": null,
  "message": "Task completed successfully",
  "context": {
    "category": "AGENT_TASK",
    "task_id": "task_12345",
    "task_type": "code_analysis",
    "duration_ms": 1450,
    "input_size": 2048,
    "output_size": 512,
    "status": "SUCCESS"
  }
}

================================================================================
4. SWARM DASHBOARD ARCHITECTURE
================================================================================

The Swarm Dashboard provides real-time visibility into the Digital Mahashakti
agent ecosystem.

------------------------------------------------------------------------------
4.1 DASHBOARD COMPONENTS
------------------------------------------------------------------------------

HEALTH PANEL
  - Agent status (online/offline/busy)
  - Heartbeat latency per agent
  - Recent failure counts
  - Resource utilization graphs

ACTIVITY STREAM
  - Real-time message flow visualization
  - Message type distribution
  - Top active agent pairs
  - Protocol error rate

TASK BOARD
  - Active task queue
  - Task assignment distribution
  - Completion rate trends
  - Bottleneck identification

CONFLICT MONITOR
  - Active conflicts
  - Resolution history
  - Voting participation rates
  - Consensus achievement time

KNOWLEDGE GRAPH
  - File sync status across DCs
  - Recent knowledge additions
  - Cross-agent knowledge sharing
  - Schema evolution tracking

------------------------------------------------------------------------------
4.2 DATA COLLECTION
------------------------------------------------------------------------------

COLLECTOR SERVICE
  Subscribes to:
    - sangam.heartbeat.>
    - sangam.event.>
    - mmkt.logs.>
    - swarm.metrics.>
  
  Aggregates:
    - Counts per agent per minute
    - Latency percentiles
    - Error rates
    - Resource trends

------------------------------------------------------------------------------
4.3 API ENDPOINTS
------------------------------------------------------------------------------

GET /api/agents
  Returns list of all agents with current status

GET /api/agents/<id>/status
  Returns detailed status for specific agent

GET /api/messages/recent
  Returns recent messages with filtering options

GET /api/tasks/active
  Returns currently executing tasks

GET /api/conflicts/open
  Returns unresolved conflicts

GET /api/metrics/system
  Returns system-wide metrics

------------------------------------------------------------------------------
4.4 DASHBOARD LAYOUT
------------------------------------------------------------------------------

+----------------------------------------------------------+
|  SWARM DASHBOARD                    [REFRESH] [SETTINGS] |
+----------------------------------------------------------+
| +------------------+  +------------------+  +----------+ |
| | HEALTH PANEL     |  | ACTIVITY STREAM  |  |  TASK    | |
| |                  |  |                  |  |  BOARD   | |
| | [agent list]     |  | [live messages]  |  | [queue]  | |
| | [status dots]    |  | [type charts]    |  | [stats]  | |
| +------------------+  +------------------+  +----------+ |
| +------------------+  +------------------+               |
| | CONFLICT MONITOR |  | KNOWLEDGE GRAPH  |               |
| |                  |  |                  |               |
| | [active]         |  | [sync status]    |               |
| | [history]        |  | [recent adds]    |               |
| +------------------+  +------------------+               |
+----------------------------------------------------------+

================================================================================
5. CONFLICT RESOLUTION SYSTEM
================================================================================

When agents disagree on decisions, the TRISHULA conflict resolution
protocol activates to achieve consensus.

------------------------------------------------------------------------------
5.1 CONFLICT TYPES
------------------------------------------------------------------------------

DECISION_CONFLICT
  Agents propose different actions for same situation
  
DATA_CONFLICT
  Agents hold contradictory information
  
PRIORITY_CONFLICT
  Agents disagree on task ordering
  
RESOURCE_CONFLICT
  Agents compete for limited resources

------------------------------------------------------------------------------
5.2 RESOLUTION STRATEGIES
------------------------------------------------------------------------------

STRATEGY_A - VOTING
  Applicable: DECISION_CONFLICT, PRIORITY_CONFLICT
  Process:
    1. Initiator declares conflict with proposals
    2. All agents vote within timeout (default: 60s)
    3. Majority wins; ties broken by seniority
    4. Dissenters may appeal with new evidence

STRATEGY_B - ARBITRATION
  Applicable: DATA_CONFLICT
  Process:
    1. Conflicting data sources identified
    2. Source trust scores compared
    3. Higher trust source prevails
    4. Lower source flagged for verification

STRATEGY_C - MERGE
  Applicable: DATA_CONFLICT (when possible)
  Process:
    1. Attempt to merge conflicting outputs
    2. If merge successful, both agents accept result
    3. If merge fails, escalate to ARBITRATION

STRATEGY_D - DELEGATION
  Applicable: All types
  Process:
    1. Conflict escalated to parent/authority agent
    2. Authority evaluates and decides
    3. Decision binding on all participants

------------------------------------------------------------------------------
5.3 CONFLICT STATE MACHINE
------------------------------------------------------------------------------

DECLARED -> [agents notified]
    |
    v
VOTING ----> [timeout reached] -> TALLY
    |                              |
    |<----- [consensus reached] ---<
    v
RESOLVED -> [outcome broadcast]
    |
    +-----> [no consensus] -> ESCALATION -> RESOLVED

------------------------------------------------------------------------------
5.4 CONFLICT MESSAGE SCHEMA
------------------------------------------------------------------------------

CONFLICT_DECLARATION
  conflict_id      : UUID
  conflict_type    : Type from 5.1
  initiator        : Agent ID
  participants     : List of involved agents
  subject          : Description of disagreement
  proposals        : Array of proposed solutions
  timestamp        : ISO-8601

VOTE_CAST
  conflict_id      : References declaration
  voter            : Agent ID
  choice           : Selected proposal index
  confidence       : 0.0 to 1.0
  reasoning        : Text explanation

CONFLICT_RESOLUTION
  conflict_id      : References declaration
  resolution_type  : VOTING/ARBITRATION/MERGE/DELEGATION
  outcome          : Winning proposal
  votes_for        : Map of agent -> choice
  resolved_at      : ISO-8601
  next_action      : What to execute

------------------------------------------------------------------------------
5.5 CONFLICT AVOIDANCE
------------------------------------------------------------------------------

PRE-SHARING
  Agents publish intentions before acting
  Others may object before work begins

SHADOW MODE
  Multiple agents solve same problem independently
  Results compared without commitment
  Best result selected, others discarded

CONFIDENCE THRESHOLDS
  Low confidence proposals trigger automatic consultation
  High confidence proposals proceed with logging only

================================================================================
6. FILE SYNC PROTOCOL (AGNI-RUSHABDEV-DC)
================================================================================

Synchronization protocol for files across three distributed computation
nodes: AGNI, RUSHABDEV, and DC (Data Center).

------------------------------------------------------------------------------
6.1 SYNC SCOPE
------------------------------------------------------------------------------

SYNCHRONIZED PATHS
  - /shared/knowledge/        - Learned patterns and rules
  - /shared/tasks/active/     - Current task assignments
  - /shared/tasks/completed/  - Task completion records
  - /shared/models/           - Shared model checkpoints
  - /shared/config/           - Configuration files

LOCAL-ONLY PATHS
  - /local/cache/             - Temporary computation cache
  - /local/logs/              - Agent-specific logs (MMKT aggregated separately)
  - /local/tmp/               - Scratch space

------------------------------------------------------------------------------
6.2 SYNC MODES
------------------------------------------------------------------------------

MODE_A - FULL_SYNC
  All files in scope synchronized bidirectionally
  Used: Initial setup, recovery, scheduled maintenance
  Trigger: Manual or scheduled every 6 hours

MODE_B - DELTA_SYNC
  Only changed files transmitted
  Used: Normal operation
  Trigger: File change event or periodic (5 minutes)

MODE_C - PUSH_ONLY
  Local changes pushed to others, no receipt
  Used: Log shipping, event publishing
  Trigger: Event-driven

MODE_D - PULL_ONLY
  Fetch remote changes, no local push
  Used: Read-only replicas, backup verification
  Trigger: On-demand or scheduled

------------------------------------------------------------------------------
6.3 FILE VERSIONING
------------------------------------------------------------------------------

VERSION VECTOR
  Each file maintains a version vector:
    {<node_id>: <sequence_number>, ...}
  
  Example: {"AGNI": 5, "RUSHABDEV": 3, "DC": 7}

CONFLICT DETECTION
  If version vectors are concurrent (neither dominates),
  a conflict exists and requires resolution.

CONFLICT RESOLUTION
  Last-Write-Wins based on timestamp
  OR semantic merge if file type supports it
  Conflict files saved as: <filename>.conflict.<node_id>.<timestamp>

------------------------------------------------------------------------------
6.4 SYNC PROTOCOL SEQUENCE
------------------------------------------------------------------------------

INITIATOR                        PEER
   |                               |
   |---SYNC_REQUEST-------------->|
   |   [manifest: file paths + hashes]
   |                               |
   |<--SYNC_RESPONSE---------------|
   |   [needs: files to transfer]
   |   [conflicts: version issues]
   |                               |
   |---SYNC_DATA----------------->|
   |   [file chunks for 'needs']
   |                               |
   |<--SYNC_CONFIRM----------------|
   |   [received + verified]
   |                               |

------------------------------------------------------------------------------
6.5 MANIFEST FORMAT
------------------------------------------------------------------------------

SYNC_MANIFEST
  protocol_version : "1.0"
  source_node      : Node ID (AGNI/RUSHABDEV/DC)
  target_node      : Node ID or "ALL"
  sync_mode        : FULL/DELTA/PUSH/PULL
  timestamp        : ISO-8601
  entries          : Array of FILE_ENTRY

FILE_ENTRY
  relative_path    : Path from sync root
  size_bytes       : File size
  content_hash     : SHA-256 of content
  modified_time    : ISO-8601
  version_vector   : {<node>: <seq>}
  is_deleted       : Boolean (tombstone)

------------------------------------------------------------------------------
6.6 NETWORK TOPOLOGY
------------------------------------------------------------------------------

          +---------+
          |   DC    |
          | (hub)   |
          +---------+
         /           \
        /             \
       v               v
  +---------+     +---------+
  |  AGNI   |<--->|RUSHABDEV|
  +---------+     +---------+

DC acts as hub for coordination
Direct links for latency-sensitive sync
Automatic fallback via DC if direct link fails

------------------------------------------------------------------------------
6.7 FAILURE HANDLING
------------------------------------------------------------------------------

NETWORK_PARTITION
  Continue local operations
  Queue sync operations
  Reconcile on reconnection

FILE_CORRUPTION
  Verify with content_hash
  Request retransmission
  Log incident to MMKT

SYNC_TIMEOUT
  Retry with exponential backoff
  Escalate to alert after 3 failures
  Switch to alternative peer if available

================================================================================
APPENDIX A: AGENT IDENTIFIERS
================================================================================

AGNI           - Analysis and Generation Node Interface
RUSHABDEV      - Resource Utilization and Shared Hash Agent
DC             - Data Center (coordinating node)
TRISHULA       - Coordination subsystem (not an agent)
MMKT           - Logging subsystem (not an agent)

================================================================================
APPENDIX B: GLOSSARY
================================================================================

SANGAM         - Message protocol (means "confluence" in Sanskrit)
TRISHULA       - Three-pronged coordination bridge (refers to trident)
MMKT           - Mahashakti Kaizen Tracking (continuous improvement logging)
DC             - Data Center (central coordination point)
NAT            - Network Address Translation / NATS messaging system
JetStream      - NATS persistence layer

================================================================================
END OF DOCUMENT
================================================================================
