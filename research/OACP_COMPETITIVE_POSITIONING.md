# OACP Competitive Positioning Analysis
## Open Agent Compute Protocol vs. Emerging Agent Standards

**Date:** February 4, 2026  
**Analyst:** OACP Competitive Intelligence Unit

---

## Executive Summary

The agent protocol landscape is rapidly crystallizing around three major standards (MCP, A2A, OpenAI's approach) plus several compute-layer alternatives (WASM, capability-based systems, blockchain/TEE). OACP's positioning depends critically on which problem it aims to solve: tool connectivity, inter-agent collaboration, compute isolation, or verifiable execution.

**Key Finding:** OACP has a strategic opportunity to occupy the **security/isolation layer** beneath MCP/A2A, providing verifiable, sandboxed compute for agent execution. This is complementary to—not competitive with—the communication protocols.

---

## 1. MCP (Model Context Protocol) — Anthropic's Standard

### Current State
- **Maturity:** MCP 2.0 (October 2025), 1,200+ servers, 73,100+ GitHub stars
- **Core Function:** Agent ↔ Tools/Data connectivity
- **Architecture:** JSON-RPC 2.0, stateful connections, capability negotiation
- **Transport:** stdio, HTTP, SSE
- **Major Adopters:** OpenAI (March 2025), Microsoft, Cloudflare

### What MCP Does Well
| Strength | Description |
|----------|-------------|
| Tool Ecosystem | Massive library of pre-built integrations (GitHub, Slack, PostgreSQL, Notion) |
| Developer Experience | FastMCP SDK auto-generates schemas from type hints + docstrings |
| User Consent | Built-in approval flows for tool execution |
| LSP Inspiration | Familiar pattern for IDE/tooling developers |

### MCP's Limitations
1. **No inter-agent communication** — designed for single agent → tools, not agent ↔ agent
2. **No execution isolation** — tools run in host environment without sandbox guarantees
3. **No verifiability** — no cryptographic proof that tool executed correctly
4. **Trust model** — relies on user consent, not technical enforcement

### OACP vs MCP Positioning

| Dimension | MCP | OACP (Proposed) |
|-----------|-----|-----------------|
| **Layer** | Application/protocol | Compute/security |
| **Scope** | Tool connectivity | Execution environment |
| **Trust model** | User consent + audit | Technical sandboxing |
| **Verifiability** | None | Cryptographic attestation |
| **Relationship** | Uses OACP for isolation | Provides isolation layer |

**Verdict:** COMPLEMENTARY — OACP provides the secure execution environment that MCP servers could run within. MCP handles the "what" (which tools), OACP handles the "how safely" (isolated, verifiable compute).

---

## 2. A2A (Agent-to-Agent) — Google/Linux Foundation

### Current State
- **Maturity:** v0.3 (July 2025), 150+ organizations, Apache 2.0
- **Core Function:** Agent ↔ Agent collaboration
- **Architecture:** JSON-RPC 2.0 over HTTP/gRPC, Protocol Buffer data model
- **Key Concepts:** Agent Cards (capability discovery), Tasks (lifecycle management), Artifacts (outputs)
- **Design Philosophy:** Opaque execution — agents collaborate without sharing internal state

### What A2A Does Well
| Strength | Description |
|----------|-------------|
| Cross-vendor interoperability | Agents from different frameworks can collaborate |
| Async-first | Native support for long-running tasks, human-in-the-loop |
| Enterprise-ready | Auth, observability, push notifications built-in |
| Modality agnostic | Text, files, structured data, forms, embedded UI |

### A2A's Limitations
1. **No execution guarantees** — relies on external trust between organizations
2. **No code isolation** — "opaque" means hidden, not necessarily secure
3. **Complexity** — three-layer architecture (data model → operations → bindings)
4. **Early stage** — still evolving, breaking changes expected

### OACP vs A2A Positioning

| Dimension | A2A | OACP (Proposed) |
|-----------|-----|-----------------|
| **Purpose** | Agent collaboration protocol | Secure compute substrate |
| **Trust boundary** | Organizational/legal | Technical/cryptographic |
| **Isolation** | None specified | Core feature |
| **Use case** | Multi-agent workflows | Untrusted agent execution |
| **Relationship** | Runs atop OACP for security | Provides foundation |

**Verdict:** COMPLEMENTARY — A2A agents could execute within OACP sandboxes, providing cryptographic proof of correct execution to counterparties without revealing internal state.

---

## 3. OpenAI Agent Protocol — Emerging Standard

### Current State
- **Approach:** Extends MCP rather than competing
- **Key Components:** Agents SDK, Apps SDK (MCP + UI), Responses API
- **Philosophy:** Simplify, standardize on MCP where possible
- **Adoption:** Integrated across ChatGPT desktop, Agents SDK, Responses API

### OpenAI's Position
- Not creating a separate protocol from scratch
- Building on MCP for tool connectivity
- Focus on developer experience and integration
- Competing at the framework level, not protocol level

### OACP vs OpenAI Positioning

**Verdict:** NEUTRAL — OpenAI's approach validates MCP. OACP would operate below this layer. If OpenAI adopts verifiable compute, they would likely use OACP or similar.

---

## 4. WASM-Based Sandboxes (Wasmtime, etc.)

### Current State
- **Maturity:** Production-ready (Wasmtime, WASI)
- **Core Function:** Language-agnostic sandboxed execution
- **Security Model:** Memory isolation, capability-based filesystem, no undefined behavior
- **Defense in depth:** Guard regions, CFI, Rust implementation

### What WASM Does Well
| Strength | Description |
|----------|-------------|
| Memory safety | Bounds checking eliminates buffer overflows |
| Control-flow integrity | Structured control flow prevents hijacking |
| Deterministic execution | Reproducible, auditable behavior |
| Near-native speed | JIT compilation with sandbox overhead < 10% |
| WASI capabilities | Fine-grained permission model |

### WASM's Limitations
1. **Not AI-native** — no built-in model serving, token management, context handling
2. **Language friction** — requires compilation to WASM, limited dynamic behavior
3. **No attestation** — no cryptographic proof of execution (alone)
4. **Tooling gaps** — debugging, profiling harder than native

### OACP vs WASM Positioning

| Dimension | WASM | OACP (Proposed) |
|-----------|------|-----------------|
| **Scope** | General compute | AI agent-specific |
| **Abstraction** | Low-level bytecode | Agent compute primitives |
| **Attestation** | None built-in | Core feature |
| **AI integration** | Manual | Native (context, models, tools) |
| **Relationship** | Implementation detail | Higher-level protocol |

**Verdict:** BUILD ON — OACP could use WASM as its isolation mechanism while adding AI-specific abstractions and attestation. WASM is a component, not a competitor.

---

## 5. Capability-Based Systems (Cap'n Proto, etc.)

### Current State
- **Maturity:** Cap'n Proto stable, ocap security model proven (E language, Sandstorm)
- **Core Function:** Secure composition of cooperating components
- **Key Insight:** "Cooperation without vulnerability" — capabilities are unforgeable references
- **Mechanism:** Per-connection capability tables, no ambient authority

### What Capability Security Does Well
| Strength | Description |
|----------|-------------|
| Principle of least authority | Components receive only needed permissions |
| Composable security | Safe to combine untrusted components |
| No confused deputy | Can't be tricked into misusing authority |
| Distributed capability transfer | CapTP protocol for network-transparent capabilities |

### Capability Limitations
1. **Conceptual overhead** — developers must think in capabilities, not ACLs
2. **Ecosystem gaps** — fewer tools than traditional security models
3. **Not AI-specific** — general-purpose security mechanism
4. **Adoption friction** — requires rethinking application architecture

### OACP vs Capability Positioning

| Dimension | Capabilities | OACP (Proposed) |
|-----------|--------------|-----------------|
| **Paradigm** | Object capabilities | Verifiable agent compute |
| **Granularity** | Object-level | Agent-level |
| **AI-native** | No | Yes |
| **Attestation** | Possible | Core feature |
| **Relationship** | Can inform design | Higher-level specialization |

**Verdict:** LEARN FROM — OACP should adopt capability principles internally while providing a more accessible interface for AI developers.

---

## 6. Blockchain/Verifiable Compute (TEE, ZK)

### Current State
- **TEE (Trusted Execution Environment):** Intel SGX, AMD SEV, ARM TrustZone, Google Confidential Computing
- **ZK (Zero-Knowledge):** Cryptographic proof of correct computation
- **Use Cases:** Dark pools, private AI inference, MEV-resistant execution
- **Trend:** Convergence of TEE + ZK for "verifiable confidential computing"

### What Verifiable Compute Does Well
| Strength | Description |
|----------|-------------|
| Cryptographic proof | Anyone can verify execution without re-running |
| Confidentiality | Private inputs, public verification |
| Decentralized trust | No single point of failure |
| Economic incentives | Can create markets for compute |

### Verifiable Compute Limitations
1. **Performance overhead** — ZK proofs expensive (orders of magnitude slower)
2. **Complexity** — Cryptographic expertise required
3. **TEE vulnerabilities** — Side-channel attacks, need for CPU-level trust
4. **Not interactive** — Poor fit for conversational agents

### OACP vs Verifiable Compute Positioning

| Dimension | Blockchain/TEE | OACP (Proposed) |
|-----------|----------------|-----------------|
| **Guarantee** | Cryptographic | Cryptographic + sandbox |
| **Performance** | Slower (ZK) | Near-native |
| **Interactivity** | Poor | Real-time capable |
| **Complexity** | High | Developer-friendly |
| **Relationship** | Can integrate | Pragmatic middle ground |

**Verdict:** HYBRID OPPORTUNITY — OACP could offer tiered guarantees: sandbox for speed, optional TEE/ZK for high-value verification. Don't compete on pure cryptography; compete on usability.

---

## OACP's Unique Value Proposition

### The Gap in Current Landscape

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT LANDSCAPE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    MCP       │  │     A2A      │  │  Frameworks  │      │
│  │  (Tools)     │  │(Inter-agent) │  │ (Pydantic,   │      │
│  │              │  │              │  │  LangGraph)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                │                    │             │
│         └────────────────┼────────────────────┘             │
│                          │                                  │
│                          ▼                                  │
│              ┌─────────────────────┐                        │
│              │   SECURITY GAP      │  ◄── OACP targets here │
│              │                     │                        │
│              │ • No isolation      │                        │
│              │ • No attestation    │                        │
│              │ • No verifiability  │                        │
│              └─────────────────────┘                        │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    WASM      │  │   TEE/ZK     │  │  Capabilities│      │
│  │ (Isolation)  │  │(Verification)│  │  (Security)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### OACP's Positioning: "The Trust Layer for Agent Compute"

**Core Thesis:** As agents gain autonomy and handle sensitive operations, the need for verifiable, sandboxed execution becomes critical. Current protocols assume trust; OACP provides it.

### Unique Value Propositions

| UVP | Current Alternative | OACP Advantage |
|-----|---------------------|----------------|
| **Agent-native isolation** | WASM + manual plumbing | Purpose-built for LLM/agent workloads |
| **Verifiable tool execution** | MCP user consent | Cryptographic proof of correct execution |
| **Cross-agent attestation** | A2A trust assumptions | Technical verification of agent behavior |
| **Composable security** | Monolithic sandboxes | Capability-based, fine-grained permissions |
| **Performance + security** | ZK (slow) or TEE (vulnerable) | WASM isolation + optional TEE attestation |

---

## Strategic Recommendations

### 1. Integrate with MCP (Don't Replace)

**Rationale:** MCP has won the tool connectivity war. Competing is futile; integration is strategic.

**Approach:**
- OACP provides `oacp-mcp-server` — a secure runtime for MCP servers
- MCP servers execute in OACP sandboxes with automatic attestation
- Existing MCP ecosystem works unchanged, gains security

**Value prop:** "Run your MCP servers in verifiable sandboxes"

### 2. Enable A2A with Attestation

**Rationale:** A2A enables multi-agent collaboration but lacks technical trust mechanisms.

**Approach:**
- OACP agents generate cryptographic attestations of their execution
- Agent Cards include OACP attestation endpoints
- Counterparties can verify behavior without trusting the operator

**Value prop:** "Cryptographically prove your agent did what it claimed"

### 3. Build on WASM + Capabilities

**Rationale:** Don't reinvent isolation; compose proven technologies.

**Approach:**
- Core: WASMtime for sandboxing
- Permissions: WASI capabilities model
- Attestation: Optional TEE integration (SGX, Confidential Computing)
- Add: AI-native primitives (context management, model APIs, tool registry)

### 4. Target High-Value Use Cases First

**Immediate opportunities:**
1. **Financial agents** — verifiable trading, audit trails
2. **Healthcare agents** — HIPAA-compliant isolated execution
3. **Enterprise automation** — SOC2-friendly agent operations
4. **Cross-organizational AI** — prove behavior to untrusted partners

### 5. Avoid Direct Competition

| Don't Compete With | Instead |
|-------------------|---------|
| MCP's ecosystem | Provide secure runtime for it |
| A2A's collaboration model | Add verification layer to it |
| WASM's isolation | Use it as foundation |
| ZK's pure cryptography | Offer pragmatic hybrid |

---

## Competitive Matrix

| Criteria | MCP | A2A | WASM | Capabilities | TEE/ZK | **OACP (Target)** |
|----------|-----|-----|------|--------------|--------|-------------------|
| **Tool connectivity** | ★★★★★ | ★★☆☆☆ | ☆☆☆☆☆ | ☆☆☆☆☆ | ☆☆☆☆☆ | ★★★★☆ |
| **Inter-agent comms** | ☆☆☆☆☆ | ★★★★★ | ☆☆☆☆☆ | ☆☆☆☆☆ | ☆☆☆☆☆ | ★★★☆☆ |
| **Execution isolation** | ☆☆☆☆☆ | ☆☆☆☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| **Cryptographic proof** | ☆☆☆☆☆ | ☆☆☆☆☆ | ☆☆☆☆☆ | ★★☆☆☆ | ★★★★★ | ★★★★☆ |
| **AI-native design** | ★★★★☆ | ★★★★☆ | ☆☆☆☆☆ | ☆☆☆☆☆ | ☆☆☆☆☆ | ★★★★★ |
| **Developer experience** | ★★★★★ | ★★★☆☆ | ★★☆☆☆ | ★★☆☆☆ | ★☆☆☆☆ | ★★★★☆ |
| **Performance** | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★☆☆☆☆ | ★★★★☆ |
| **Maturity** | ★★★★★ | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |

---

## Conclusion

**OACP should position as the security/trust layer beneath MCP and A2A**, not as a competing communication protocol. The winning strategy:

1. **Build on WASM** for isolation (don't reinvent)
2. **Integrate with MCP** for tool ecosystem (don't compete)
3. **Enable A2A** with attestation (add value)
4. **Target high-value domains** where trust is critical (financial, healthcare, enterprise)

The agent ecosystem needs a "trust layer" — OACP can be that layer while letting MCP and A2A handle the "connection layer."

**Bottom line:** Be the Linux kernel, not the HTTP protocol. Everything runs on you, but users interact with the layers above.

---

*Analysis completed February 4, 2026*
