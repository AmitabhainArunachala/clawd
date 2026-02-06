# OACP v0.2 Roadmap
## Operational Agent Control Protocol - Version 0.2 Design Specification

**Role:** OACP_V02_ROADMAPPER  
**Date:** February 5, 2026  
**Status:** Draft for Review  

---

## Executive Summary

OACP v0.2 represents the transition from prototype to production-ready infrastructure. Based on v0.1 concepts and competitive landscape analysis, v0.2 focuses on four pillars: **Security** (real sandboxing), **Interoperability** (MCP/A2A integration), **Performance** (async I/O, batching), and **Verifiability** (ACP attestation framework).

**Critical Path:** Without v0.2's MUST HAVE features, OACP cannot serve as a trust layer for production agent systems.

---

## 1. MUST FIX Before Real Use (Critical Blockers)

### 1.1 The Airlock Implementation — Core Security Layer
**Priority:** 🔴 MUST HAVE  
**Current State:** Conceptual in v0.1  
**Target:** Production-ready isolation

#### Decision: WASM + gVisor Hybrid

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Core Sandbox** | Wasmtime (WASM) | Memory-safe, deterministic, near-native speed |
| **System Call Filter** | gVisor / seccomp-bpf | Defense in depth for filesystem/network |
| **Container Boundary** | Firecracker microVMs | Lightweight VM isolation for untrusted code |
| **Network Isolation** | Slirp4netns + iptables | User-space networking with policy control |

**Why Not Just Docker?**
- Docker shares kernel → container escape risks
- OACP needs defense-in-depth: WASM (app) → gVisor (syscall) → Firecracker (VM)
- Each layer is independently auditable

**Architecture:**
```
┌─────────────────────────────────────────────┐
│           OACP Airlock v0.2                 │
├─────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌─────────┐ │
│  │  Agent    │  │   Tool    │  │ Context │ │
│  │  WASM     │  │   WASM    │  │  Store  │ │
│  │  Module   │  │   Module  │  │ (WASM)  │ │
│  └─────┬─────┘  └─────┬─────┘  └────┬────┘ │
│        └──────────────┼─────────────┘       │
│                       ▼                     │
│  ┌─────────────────────────────────────────┐│
│  │      OACP Runtime (Rust/Go)            ││
│  │  • WASI interfaces (filesystem, clock) ││
│  │  • Capability management               ││
│  │  • Resource quotas (CPU, memory, I/O)  ││
│  └─────────────────────────────────────────┘│
│                       │                     │
│        ┌──────────────┼──────────────┐      │
│        ▼              ▼              ▼      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  gVisor  │  │ Network  │  │  TEE     │  │
│  │  Sentry  │  │  Policy  │  │  (opt)   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                       │                     │
│                       ▼                     │
│  ┌─────────────────────────────────────────┐│
│  │     Firecracker MicroVM (optional)     ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

#### Deliverables:
1. **Airlock Core** (`airlock/` crate/package)
   - WASM module loader with WASI Preview 2
   - Capability-based permission system
   - Resource quota enforcement (cgroup integration)
   
2. **Tool Sandbox** (`airlock/tool-runner`)
   - Run untrusted MCP servers in isolation
   - Automatic capability discovery from manifest
   - Network egress filtering

3. **Agent Sandbox** (`airlock/agent-runner`)
   - Full agent execution environment
   - Context isolation between agents
   - State checkpointing for resumption

---

### 1.2 Secure Context Isolation
**Priority:** 🔴 MUST HAVE  
**Problem:** v0.1 agents share context space — leaks between untrusted agents  
**Solution:** Hardware-backed context partitioning

**Implementation:**
```rust
pub struct ContextVault {
    // Each agent gets its own encrypted context partition
    partitions: HashMap<AgentId, ContextPartition>,
    // Master key in HSM/TEE, never leaves secure enclave
    master_key: ProtectedKey,
}

pub struct ContextPartition {
    agent_id: AgentId,
    encryption_key: DerivedKey,  // HKDF from master + agent_id
    access_log: AppendOnlyLog,   // Audit trail
    quota: ResourceQuota,        // Memory, tokens, disk
}
```

**Security Properties:**
- Context encrypted at rest (AES-256-GCM)
- Keys derived per-agent, no key reuse
- Memory isolation via WASM sandbox
- Access logging for audit

---

### 1.3 Resource Quotas & DoS Protection
**Priority:** 🔴 MUST HAVE  
**Missing in v0.1:** No limits on agent CPU, memory, tokens, API calls

**Quota System:**
| Resource | Default Limit | Enforced By |
|----------|---------------|-------------|
| CPU time | 1 core-second/request | WASM fuel metering |
| Memory | 512 MB | Wasmtime memory limits |
| Disk I/O | 10 MB/s | cgroup blkio |
| Network | 100 req/min | Token bucket |
| LLM tokens | 100k/request | OACP proxy |
| API calls | 1000/hour | Quota service |

**Implementation:**
- Pre-flight quota check
- Real-time consumption tracking
- Hard cutoff when exceeded (no grace)
- Burst allowance with decay

---

### 1.4 Cryptographic Identity & Authentication
**Priority:** 🔴 MUST HAVE  
**v0.1 Gap:** No way to prove which agent performed an action

**OACP Identity Stack:**
```
┌─────────────────────────────────────────┐
│  Agent Identity (Ed25519 keypair)      │
│  • Generated in TEE or HSM at creation │
│  • Public key = Agent ID               │
├─────────────────────────────────────────┤
│  Session Keys (X25519 ephemeral)       │
│  • Rotated every 15 minutes            │
│  • Forward secrecy                     │
├─────────────────────────────────────────┤
│  Attestation Keys (TPM/TEE)            │
│  • Platform attestation (optional)     │
│  • Remote attestation to verifiers     │
└─────────────────────────────────────────┘
```

**All messages signed:** `signature = ed25519_sign(agent_key, hash(payload + timestamp + nonce))`

---

## 2. Missing Features for Production

### 2.1 MCP Integration Layer
**Priority:** 🔴 MUST HAVE  
**Rationale:** MCP has the ecosystem; OACP must integrate, not compete

**Architecture:**
```
┌──────────────────────────────────────────────────────┐
│                  MCP Client (Agent)                  │
├──────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────┐  │
│  │         OACP-MCP Bridge                        │  │
│  │  ┌─────────────┐      ┌─────────────────────┐  │  │
│  │  │ MCP Protocol│◄────►│  Capability Manager │  │  │
│  │  │  Adapter    │      │  (What tools allowed│  │  │
│  │  └─────────────┘      └─────────────────────┘  │  │
│  │         │                                       │  │
│  │         ▼                                       │  │
│  │  ┌─────────────────────────────────────────────┐│  │
│  │  │      Airlock (Isolated Runtime)            ││  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ ││  │
│  │  │  │MCP Server│  │MCP Server│  │MCP Server│ ││  │
│  │  │  │  (git)   │  │ (slack)  │  │ (custom) │ ││  │
│  │  │  └──────────┘  └──────────┘  └──────────┘ ││  │
│  │  └─────────────────────────────────────────────┘│  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

**Features:**
1. **MCP Server Registry**
   - Curated, audited MCP servers in OACP format
   - Automatic sandbox packaging
   - Reputation scoring

2. **Capability Negotiation**
   - Agent requests tool X with permissions {read, write}
   - User approves via OACP consent UI
   - Capabilities enforced by Airlock

3. **Tool Execution Attestation**
   - Every tool call logged with cryptographic proof
   - Result signed by executing sandbox
   - Verifiable by third parties

---

### 2.2 A2A Integration with Attestation
**Priority:** 🟡 SHOULD HAVE  
**Value:** Enable trustless multi-agent collaboration

**OACP Enhancement to A2A:**
| Standard A2A | OACP-Enhanced A2A |
|--------------|-------------------|
| Agent Card (JSON) | Agent Card + Attestation Endpoint |
| Task submission | Signed task with execution proof |
| Artifact exchange | Encrypted, attestable artifacts |
| Trust via reputation | Trust via cryptographic verification |

**Attestation Flow:**
```
Agent A                    OACP Node A              OACP Node B              Agent B
  │                            │                        │                        │
  │─Execute Task──────────────►│                        │                        │
  │                            │─Run in Airlock───────►│                        │
  │                            │◄─Attestation──────────│                        │
  │◄─Result + Proof────────────│                        │                        │
  │                            │                        │                        │
  │─Send to Agent B (A2A)──────┼───────────────────────►│─Verify attestation────►│
  │                            │                        │◄─Trust established─────│
  │◄───────────────────────────┼────────────────────────┼─Process task───────────│
```

---

### 2.3 Distributed OACP Nodes
**Priority:** 🟡 SHOULD HAVE  
**Use Case:** Enterprise deployments, edge computing, cross-region agents

**Architecture: Federated OACP Mesh**
```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  OACP Node    │◄────►│  OACP Node    │◄────►│  OACP Node    │
│  (us-east)    │      │  (eu-west)    │      │  (ap-south)   │
│               │      │               │      │               │
│ ┌───────────┐ │      │ ┌───────────┐ │      │ ┌───────────┐ │
│ │ Airlock   │ │      │ │ Airlock   │ │      │ │ Airlock   │ │
│ │ Registry  │ │      │ │ Registry  │ │      │ │ Registry  │ │
│ └───────────┘ │      │ └───────────┘ │      │ └───────────┘ │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Consensus Layer    │
                    │  (etcd/Raft)        │
                    │  • Agent placement  │
                    │  • Quota federation │
                    │  • Attestation root │
                    └─────────────────────┘
```

**Node-to-Node Protocol:**
- gRPC with mutual TLS
- Capability token exchange
- Agent migration with encrypted state transfer
- Quota pooling for multi-node deployments

---

### 2.4 Observability Stack
**Priority:** 🔴 MUST HAVE  
**What's Missing:** No visibility into agent behavior, resource usage, security events

**Components:**

| Layer | Tool | Purpose |
|-------|------|---------|
| Metrics | Prometheus | Resource usage, performance |
| Logging | OpenTelemetry | Structured, queryable logs |
| Tracing | Jaeger/Tempo | Distributed request tracing |
| Alerting | AlertManager | Anomaly detection |
| Dashboard | Grafana | Operational visibility |

**OACP-Specific Metrics:**
```
oacp_agents_running{agent_id, node}
oacp_tool_calls_total{tool, agent, status}
oacp_quota_consumed{resource, agent}
oacp_attestations_generated{agent}
oacp_security_events_total{severity, type}
oacp_context_operations_total{operation, agent}
```

---

### 2.5 Policy Engine
**Priority:** 🟡 SHOULD HAVE  
**Use Case:** Enterprise governance, compliance rules

**Policy Language (Rego/OPA):**
```rego
# Example: HIPAA compliance policy
package oacp.hipaa

default allow = false

# Allow read of patient data only by authorized agents
allow {
    input.action == "read"
    input.resource.type == "patient_data"
    input.agent.attributes.authorized_for_hipaa == true
    input.agent.attestation.level >= "moderate"
}

# Deny all data export to external systems
deny {
    input.action == "write"
    input.resource.location == "external"
}
```

---

## 3. The Real Airlock Implementation

### 3.1 Why WASM + Not Docker Alone

| Concern | Docker | WASM (Wasmtime) |
|---------|--------|-----------------|
| Startup time | Seconds | Milliseconds |
| Memory overhead | 10-100 MB | 1-10 MB |
| Attack surface | Kernel + container runtime | User-space only |
| Determinism | No (kernel-dependent) | Yes (defined behavior) |
| Cross-platform | Image-based | Bytecode (run anywhere) |
| AI-native | No | Yes (with WASI-NN) |

**Decision:** WASM for compute, Docker for Airlock control plane only

### 3.2 Airlock Implementation Phases

**Phase 1: Core Sandbox (MVP)**
- Wasmtime integration
- WASI Preview 2 interfaces
- Basic capability system

**Phase 2: Hardening**
- gVisor syscall filtering
- Network namespace isolation
- Seccomp-BPF profiles

**Phase 3: Enterprise**
- Firecracker microVM option
- TEE integration (SGX/SEV)
- FIPS 140-2 compliance mode

---

## 4. Network Support — Distributed OACP

### 4.1 Node Discovery
```rust
pub struct NodeDiscovery {
    // Bootstrap via DNS, Consul, or static config
    bootstrap: Vec<SocketAddr>,
    // Gossip protocol for node health
    gossip: GossipProtocol,
    // DHT for agent location lookup
    routing: KademliaDHT,
}
```

### 4.2 Agent Mobility
Agents can migrate between nodes:
1. Serialize agent state (encrypted)
2. Transfer to target node
3. Resume in Airlock at new node
4. Update routing table

### 4.3 Quota Federation
```rust
pub struct FederatedQuota {
    // Local quota on this node
    local: ResourceQuota,
    // Delegated quota from other nodes
    delegated: Vec<(NodeId, ResourceQuota)>,
    // Quota lent to other nodes
    lent: Vec<(NodeId, ResourceQuota)>,
}
```

---

## 5. ACP (Attested Compliance Profile)

### 5.1 What is ACP?
A cryptographic attestation of an agent's compliance with a policy profile. Think "TLS certificate for agent behavior."

### 5.2 ACP Structure
```json
{
  "acp_version": "0.2.0",
  "profile_id": "hipaa-compliant-agent-v1",
  "agent_id": "ed25519:abc123...",
  "attestation": {
    "timestamp": "2026-02-05T00:00:00Z",
    "nonce": "random-256-bits",
    "platform": {
      "type": "oacp-airlock-v0.2",
      "tee_type": "intel-sgx",
      "quote": "base64-encoded-sgx-quote",
      "measurement": "sha256-of-airlock-config"
    },
    "execution": {
      "tool_calls": [
        {
          "tool": "filesystem/read",
          "allowed": true,
          "path": "/data/patient/12345",
          "hash": "sha256-of-result"
        }
      ],
      "policy_checks": [
        {
          "policy": "hipaa-data-access",
          "result": "pass",
          "evidence_hash": "sha256-of-evidence"
        }
      ]
    }
  },
  "signatures": {
    "agent": "ed25519-sig-of-attestation",
    "airlock": "ed25519-sig-by-airlock-key",
    "tee": "optional-tee-signature"
  }
}
```

### 5.3 ACP Verification
```rust
pub fn verify_acp(acp: &ACP, policy: &Policy) -> Result<TrustLevel, VerificationError> {
    // 1. Verify signatures
    verify_signatures(acp)?;
    
    // 2. Verify TEE quote (if present)
    if let Some(tee) = &acp.attestation.platform.tee {
        verify_tee_quote(tee)?;
    }
    
    // 3. Check policy compliance
    for check in &acp.attestation.execution.policy_checks {
        if check.result != "pass" {
            return Err(PolicyViolation(check.policy.clone()));
        }
    }
    
    // 4. Calculate trust score
    let score = calculate_trust(acp);
    Ok(score)
}
```

### 5.4 Trust Levels
| Level | Requirements | Use Case |
|-------|--------------|----------|
| 🔴 Untrusted | No ACP | Development only |
| 🟡 Basic | Agent signature only | Internal tools |
| 🟢 Standard | Agent + Airlock signatures | Production agents |
| 🔵 Verified | + TEE attestation | Financial, healthcare |
| 🟣 Maximum | + Multi-party attestation | Critical infrastructure |

---

## 6. MCP Integration — Adapter Layer

### 6.1 OACP-MCP Bridge Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    OACP-MCP Bridge                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              MCP Protocol Layer                        │  │
│  │  • JSON-RPC 2.0 over stdio/HTTP/SSE                   │  │
│  │  • Tool discovery and capability negotiation          │  │
│  │  • Request/response routing                           │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌─────────────────────────┼─────────────────────────────┐  │
│  │         OACP Translation Layer                         │  │
│  │  ┌─────────────────────┐  ┌─────────────────────────┐ │  │
│  │  │   Tool Manifest     │  │   Capability Mapping    │ │  │
│  │  │   Converter         │  │   (MCP caps → OACP caps)│ │  │
│  │  └─────────────────────┘  └─────────────────────────┘ │  │
│  │  ┌─────────────────────┐  ┌─────────────────────────┐ │  │
│  │  │   Execution Wrapper │  │   Attestation Generator │ │  │
│  │  │   (sandboxes tool)  │  │   (creates ACP proofs)  │ │  │
│  │  └─────────────────────┘  └─────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌─────────────────────────▼─────────────────────────────┐  │
│  │                Airlock Runtime                         │  │
│  │         (Isolated MCP server execution)                │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Running Existing MCP Servers in OACP

**Automatic Packaging:**
```bash
# OACP analyzes MCP server and creates sandboxed version
oacp mcp package ./my-mcp-server

# Generates:
# - WASM wrapper (if TypeScript/Python)
# - Capability manifest (from code analysis)
# - Sandboxed filesystem layout
# - Network policy (allowlist egress)
```

**Execution:**
```bash
# Run MCP server in OACP Airlock
oacp mcp run ./my-mcp-server \
  --allow-files=/tmp/workdir \
  --allow-network=api.github.com:443 \
  --quota-memory=256mb \
  --attest-level=standard
```

### 6.3 Native OACP Tools (Future)
Tools built specifically for OACP (better performance, native attestation):
```rust
#[oacp_tool]
fn search_documents(query: &str, context: &Context) -> Result<Vec<Document>, Error> {
    // Runs natively in Airlock
    // Automatic attestation generation
    // Fine-grained capability model
}
```

---

## 7. Performance Enhancements

### 7.1 Async I/O Architecture
**Current (v0.1):** Synchronous, blocking  
**Target (v0.2):** Full async/await with Tokio

```rust
pub struct OACPRuntime {
    // Tokio runtime for async execution
    executor: Runtime,
    // Concurrent agent execution
    agent_handles: HashMap<AgentId, JoinHandle<()>>,
    // Async I/O for tools
    tool_clients: HashMap<ToolId, ToolClient>,
}

impl OACPRuntime {
    pub async fn execute_agent(&self, agent: Agent) -> Result<Execution, Error> {
        // Concurrent tool calls
        let results = futures::join_all(
            agent.tool_calls.iter().map(|tc| self.call_tool(tc))
        ).await;
        
        // Async context operations
        let context = self.context.read(&agent.context_id).await?;
        
        Ok(Execution::new(results, context))
    }
}
```

### 7.2 Batch Processing
**Use Case:** High-throughput agent farms, data processing

```rust
pub struct BatchExecutor {
    // Group similar requests
    batcher: RequestBatcher,
    // LLM API batching (cheaper per-token)
    llm_batch_size: usize,
    // Tool call batching
    tool_batch_size: usize,
}

// Example: Batch 100 agent requests into single LLM call
let results = batch_executor
    .with_llm_batch_size(100)
    .with_tool_batch_size(50)
    .execute(agent_requests)
    .await?;
```

**Benefits:**
- 50-70% cost reduction on LLM APIs
- Better cache utilization
- Reduced latency for bursty workloads

### 7.3 Connection Pooling
```rust
pub struct ConnectionPool {
    // Pool LLM API connections
    llm_pools: HashMap<Provider, Pool<LLMClient>>,
    // Pool database connections
    db_pools: HashMap<Database, Pool<DbClient>>,
    // Pool tool HTTP clients
    http_pools: HashMap<ToolId, Pool<HttpClient>>,
}
```

### 7.4 Performance Targets

| Metric | v0.1 | v0.2 Target |
|--------|------|-------------|
| Agent startup | 5-10s | <100ms |
| Tool call latency | 2-5s | <500ms |
| Concurrent agents | 10 | 1000+ |
| Context read | 100ms | <10ms |
| Throughput (req/s) | 10 | 1000+ |
| Memory/agent | 100 MB | <10 MB |

---

## Prioritized Roadmap

### Phase 1: Foundation (Weeks 1-4) 🔴 MUST HAVE
| Feature | Effort | Owner | Deliverable |
|---------|--------|-------|-------------|
| Airlock Core (Wasmtime) | 2w | @security-team | `airlock/` crate |
| Resource Quotas | 1w | @runtime-team | Quota service |
| Cryptographic Identity | 1w | @crypto-team | Identity service |
| Secure Context Isolation | 1w | @storage-team | ContextVault |

### Phase 2: Integration (Weeks 5-8) 🔴 MUST HAVE
| Feature | Effort | Owner | Deliverable |
|---------|--------|-------|-------------|
| MCP Bridge | 2w | @integration-team | `oacp-mcp` crate |
| ACP Framework | 2w | @crypto-team | ACP spec + impl |
| Observability Stack | 1w | @platform-team | Metrics, logs, traces |
| Policy Engine (basic) | 1w | @security-team | OPA integration |

### Phase 3: Scale (Weeks 9-12) 🟡 SHOULD HAVE
| Feature | Effort | Owner | Deliverable |
|---------|--------|-------|-------------|
| Async I/O Migration | 2w | @runtime-team | Full async runtime |
| Batch Processing | 1w | @performance-team | BatchExecutor |
| Distributed Nodes | 2w | @distributed-team | Node protocol |
| A2A Attestation | 1w | @integration-team | A2A extensions |

### Phase 4: Hardening (Weeks 13-16) 🟢 NICE TO HAVE
| Feature | Effort | Owner | Deliverable |
|---------|--------|-------|-------------|
| TEE Integration | 2w | @security-team | SGX/SEV support |
| Firecracker MicroVMs | 1w | @security-team | VM backend |
| Advanced Policy Engine | 1w | @security-team | Custom policies |
| Performance Optimization | 2w | @performance-team | Benchmarks, tuning |

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| WASM adoption friction | High | Provide native bindings for TS/Python |
| MCP ecosystem changes | Medium | Design for spec evolution |
| Performance overhead | Medium | Benchmark early, optimize hot paths |
| TEE complexity | Low | Make optional, not required |
| Key management | High | HSM integration, clear custody model |

---

## Success Criteria for v0.2

1. **Security:** Passes independent security audit
2. **Performance:** 10x improvement in throughput vs v0.1
3. **Adoption:** Can run top 20 MCP servers in Airlock
4. **Verification:** ACP attestation verifiable by third parties
5. **Scale:** Production-ready for 100+ concurrent agents

---

## Appendix A: Tech Stack Summary

| Component | Technology |
|-----------|------------|
| Language | Rust (core), Go (control plane), Python (SDK) |
| Sandbox | Wasmtime + WASI Preview 2 |
| Isolation | gVisor + seccomp-bpf |
| VM (optional) | Firecracker |
| Crypto | Ring (Rust), Ed25519, X25519 |
| Networking | Tokio, gRPC, QUIC |
| Storage | SQLite (embedded), PostgreSQL (clustered) |
| Observability | OpenTelemetry, Prometheus, Grafana |
| Policy | Open Policy Agent (OPA) |

---

*Document Version: 0.2.0-draft  
Last Updated: February 5, 2026  
Next Review: Post-Phase 1 Completion*
