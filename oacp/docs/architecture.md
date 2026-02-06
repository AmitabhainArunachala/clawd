# OACP Architecture Overview

**Understanding how OACP provides verifiable, sandboxed agent compute.**

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER APPLICATION                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │   MCP Client    │  │   A2A Client    │  │    Direct OACP SDK      │  │
│  │ (Claude, etc.)  │  │ (Agent network) │  │      Integration        │  │
│  └────────┬────────┘  └────────┬────────┘  └────────────┬────────────┘  │
└───────────┼────────────────────┼────────────────────────┼───────────────┘
            │                    │                        │
            └────────────────────┼────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    OACP GATEWAY         │
                    │  • Protocol adapter     │
                    │  • Request routing      │
                    │  • Policy enforcement   │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   SANDBOX 1   │      │    SANDBOX 2    │      │    SANDBOX N    │
│ ┌───────────┐ │      │ ┌─────────────┐ │      │ ┌─────────────┐ │
│ │ WASM      │ │      │ │ WASM        │ │      │ │ WASM        │ │
│ │ Runtime   │ │      │ │ Runtime     │ │      │ │ Runtime     │ │
│ ├───────────┤ │      │ ├─────────────┤ │      │ ├─────────────┤ │
│ │ Agent     │ │      │ │ Agent       │ │      │ │ Agent       │ │
│ │ Container │ │      │ │ Container   │ │      │ │ Container   │ │
│ ├───────────┤ │      │ ├─────────────┤ │      │ ├─────────────┤ │
│ │ Tool      │ │      │ │ Tool        │ │      │ │ Tool        │ │
│ │ Registry  │ │      │ │ Registry    │ │      │ │ Registry    │ │
│ └───────────┘ │      │ └─────────────┘ │      │ └─────────────┘ │
└───────┬───────┘      └────────┬────────┘      └────────┬────────┘
        │                       │                        │
        └───────────────────────┼────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   ATTESTATION LAYER    │
                    │  • Execution logs      │
                    │  • Cryptographic proof │
                    │  • Signature chain     │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  VERIFICATION REGISTRY │
                    │  (Distributed/Local)   │
                    └────────────────────────┘
```

---

## Core Components

### 1. OACP Gateway

The entry point for all OACP operations. Acts as protocol adapter and policy enforcer.

**Responsibilities:**
- Accept requests from MCP, A2A, or direct SDK calls
- Authenticate and authorize requests
- Route to appropriate sandbox
- Enforce global policies

```python
from oacp import Gateway

gateway = Gateway.create(
    policies=[
        Policy.max_sandboxes(10),
        Policy.require_attestation(),
        Policy.network_isolation(),
    ]
)
```

---

### 2. Sandbox

Isolated execution environment using WASM + optional TEE.

**Layers:**

```
┌─────────────────────────────────────┐
│  AGENT CODE (User-provided)         │  ← Python/JS executed via WASM
├─────────────────────────────────────┤
│  OACP RUNTIME                       │  ← Context management, tool registry
├─────────────────────────────────────┤
│  WASM RUNTIME (Wasmtime)            │  ← Memory isolation, capability-based FS
├─────────────────────────────────────┤
│  WASI CAPABILITIES                  │  ← Fine-grained permission model
├─────────────────────────────────────┤
│  HOST OS / CONTAINER (Optional)     │  ← Docker for additional isolation
├─────────────────────────────────────┤
│  HARDWARE TEE (Optional SGX/CC)     │  ← Cryptographic execution proof
└─────────────────────────────────────┘
```

**Sandbox Types:**

| Type | Isolation | Attestation | Use Case |
|------|-----------|-------------|----------|
| `LIGHT` | Process only | Basic hash | Development |
| `STANDARD` | WASM sandbox | Execution proof | Production |
| `HARDENED` | WASM + Docker | Full chain | High-security |
| `TEE` | SGX/Confidential | HW attestation | Maximum trust |

---

### 3. Attestation Layer

Generates cryptographic proof of execution.

**Attestation Structure:**

```python
@dataclass
class Attestation:
    # Identity
    sandbox_id: str
    execution_id: str
    timestamp: datetime
    
    # Code provenance
    agent_hash: str  # SHA-256 of agent code
    tool_hashes: dict[str, str]  # Tool code hashes
    
    # Execution log
    input_hash: str
    output_hash: str
    tool_calls: list[ToolCall]
    
    # Cryptographic proof
    signature: bytes  # Signed by sandbox
    tee_quote: Optional[bytes]  # Hardware attestation (if TEE)
```

**Verification Chain:**

```
User Request → Sandbox Execution → Attestation Generation → Registry Storage
                                                    ↓
Third Party Verification ← Signature Validation ← Registry Lookup
```

---

### 4. Tool Registry

Manages sandboxed tool execution with capability-based permissions.

**Tool Lifecycle:**

```
Tool Registration → Capability Grant → Sandbox Binding → Execution
       ↓                   ↓                ↓              ↓
   Schema validation   Permission map   WASM compile   Logged + Attested
```

**Capability Model:**

```python
# Tools receive only explicitly granted capabilities
tool_capabilities = {
    "file_read": ["/data/allowed/*"],
    "file_write": [],  # No write access
    "network": ["api.trusted.com:443"],
    "env": ["USER", "HOME"],
}
```

---

## Data Flow

### Standard Execution Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────►│ Gateway │────►│ Sandbox │────►│  Agent  │────►│  Tool   │
│ Request │     │ Validate│     │  Spawn  │     │  Run    │     │  Call   │
└─────────┘     └─────────┘     └─────────┘     └─────────┘     └────┬────┘
                                                                     │
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐         │
│  User   │◄────│ Registry│◄────│ Attest  │◄────│  Tool   │◄────────┘
│ Response│     │ Storage │     │ Generate│     │ Result  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

### Verification Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Verifier   │────►│  Registry   │────►│   Sandbox   │────►│    TEE      │
│  Request    │     │   Lookup    │     │   Public    │     │  Provider   │
│             │     │             │     │    Key      │     │  (if used)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                                                                   │
       └───────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │ Signature Valid │
                            │ Execution Proof │
                            │ Time Validity   │
                            └─────────────────┘
```

---

## Integration Patterns

### Pattern 1: OACP + MCP (Recommended)

MCP handles tool connectivity; OACP provides secure execution.

```python
from oacp import Sandbox
from oacp.integrations.mcp import OACPMCPServer

# Create OACP sandbox
sandbox = Sandbox.create(name="mcp-secure")

# Wrap existing MCP server with OACP attestation
secure_server = OACPMCPServer(
    server_path="./mcp-server.py",
    sandbox=sandbox,
)

# All tool calls now include OACP attestations
```

**Benefits:**
- Existing MCP ecosystem works unchanged
- Gains verifiable execution
- No code changes to MCP servers

---

### Pattern 2: OACP + A2A

A2A handles agent collaboration; OACP provides trust.

```python
from oacp import Agent, AttestationLevel
from oacp.integrations.a2a import OACPAgentCard

# Create agent with attestation
agent = Agent(
    name="trading-agent",
    attestation=AttestationLevel.FULL,
)

# A2A Agent Card includes attestation endpoint
card = OACPAgentCard(
    agent=agent,
    attestation_endpoint="https://oacp.example.com/attest",
)

# Counterparties can verify all behavior cryptographically
```

**Benefits:**
- Cross-agent trust without organizational reliance
- Cryptographic proof of behavior
- Verifiable compliance

---

### Pattern 3: Direct OACP SDK

Build directly on OACP primitives.

```python
from oacp import Sandbox, Agent, Policy

# Full control over sandbox configuration
sandbox = Sandbox.create(
    name="custom",
    wasm_config=WasmConfig(
        memory_limit_mb=512,
        cpu_quota_ms=1000,
    ),
    policies=[
        Policy.network_allowlist(["api.example.com"]),
        Policy.file_readonly("/data"),
    ],
    tee=TEEConfig(provider="intel_sgx"),
)

agent = Agent(sandbox=sandbox)
```

---

## Security Layers

```
┌────────────────────────────────────────────────────────────┐
│ LAYER 6: APPLICATION                                        │
│ - Agent code validation                                     │
│ - Input/output sanitization                                 │
│ - Business logic verification                               │
├────────────────────────────────────────────────────────────┤
│ LAYER 5: TOOL REGISTRY                                      │
│ - Capability-based access control                           │
│ - Tool schema validation                                    │
│ - Execution logging                                         │
├────────────────────────────────────────────────────────────┤
│ LAYER 4: OACP RUNTIME                                       │
│ - Context isolation                                         │
│ - Attestation generation                                    │
│ - Policy enforcement                                        │
├────────────────────────────────────────────────────────────┤
│ LAYER 3: WASM RUNTIME                                       │
│ - Memory sandboxing                                         │
│ - Control-flow integrity                                    │
│ - WASI capabilities                                         │
├────────────────────────────────────────────────────────────┤
│ LAYER 2: CONTAINER (optional)                               │
│ - Process isolation                                         │
│ - Filesystem sandboxing                                     │
│ - Network namespaces                                        │
├────────────────────────────────────────────────────────────┤
│ LAYER 1: HARDWARE TEE (optional)                            │
│ - Confidential computing                                    │
│ - Remote attestation                                        │
│ - Memory encryption                                         │
└────────────────────────────────────────────────────────────┘
```

---

## Scalability Architecture

### Single Node

```
┌─────────────────────────────────────┐
│           OACP Node                 │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│  │GW   │ │S1   │ │S2   │ │S3   │   │
│  │     │ │     │ │     │ │     │   │
│  └─────┘ └─────┘ └─────┘ └─────┘   │
│       \/                            │
│  ┌─────────────────────────────┐    │
│  │      Local Registry         │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

### Multi-Node (Federated)

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Node A     │◄────►│   Node B     │◄────►│   Node C     │
│  (US-East)   │      │  (EU-West)   │      │  (APAC)      │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Global Registry │
                    │  (Consensus)     │
                    └─────────────────┘
```

---

## Configuration Reference

### Sandbox Configuration

```yaml
# oacp.yaml
sandbox:
  default_type: "standard"
  
  wasm:
    runtime: "wasmtime"
    memory_limit_mb: 512
    cpu_quota_ms: 1000
    
  capabilities:
    file_read: ["/data/*"]
    file_write: ["/tmp/*"]
    network:
      allowlist: ["*.trusted.com"]
      denylist: ["169.254.0.0/16"]
    env: ["USER", "HOME", "OACP_*"]
    
  tee:
    enabled: true
    provider: "intel_sgx"  # or "amd_sev", "azure_cc"
    
attestation:
  level: "full"
  registry: "https://oacp-registry.example.com"
  retention_days: 90
```

---

## Comparison with Related Technologies

| Dimension | Docker | WASM | TEE | OACP |
|-----------|--------|------|-----|------|
| **Isolation** | Process | Memory + Control Flow | Hardware | All layers |
| **Attestation** | None | None | Hardware quote | Cryptographic chain |
| **AI-Native** | No | No | No | Yes |
| **Tool Verification** | No | No | Limited | Full provenance |
| **Performance** | Near-native | Near-native | 5-20% overhead | WASM + 5% |
| **Developer Experience** | Good | Medium | Poor | Excellent |

---

## Next Steps

- **[API Reference](./api/README.md)** — Complete API documentation
- **[Security Guide](./security/considerations.md)** — Production security
- **[Migration Guide](./migration.md)** — Move from ungated to OACP
