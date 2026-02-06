# OACP Quickstart Guide

**Get your first OACP-gated agent running in 5 minutes.**

---

## What You'll Build

A simple agent that runs inside an OACP sandbox with cryptographic attestation. By the end, you'll:

1. Install OACP runtime
2. Create a sandboxed agent
3. Execute a tool with verifiable proof
4. Verify the attestation

---

## Prerequisites

- Python 3.11+ or Node.js 20+
- Docker (recommended for sandbox isolation)
- 5 minutes

---

## Step 1: Install OACP (60 seconds)

```bash
# Python
pip install oacp-sdk

# Node.js
npm install @oacp/sdk
```

Verify installation:

```bash
oacp --version
# Output: oacp-sdk 0.1.0
```

---

## Step 2: Create Your First Sandbox (90 seconds)

Create `hello_oacp.py`:

```python
from oacp import Sandbox, Agent, AttestationLevel

# Create a sandbox with default security settings
sandbox = Sandbox.create(
    name="hello-world",
    attestation=AttestationLevel.BASIC,  # Cryptographic proof of execution
)

# Define a simple agent
agent = Agent(
    name="greeter",
    model="claude-sonnet-4-0",
    sandbox=sandbox,
)

# Run the agent
result = agent.run("Say hello to OACP!")
print(result.output)
# Output: Hello! I'm running inside an OACP-verified sandbox.

# Verify the attestation
print(f"Attestation: {result.attestation.signature[:32]}...")
print(f"Sandbox ID: {result.sandbox_id}")
```

Run it:

```bash
python hello_oacp.py
```

**What just happened?**
- OACP spawned an isolated WASM sandbox
- Your agent executed inside the sandbox
- OACP generated a cryptographic attestation proving:
  - The code that ran (hash of agent)
  - The inputs provided
  - The outputs produced
  - The sandbox configuration

---

## Step 3: Add a Tool with Verification (90 seconds)

Create `tool_example.py`:

```python
from oacp import Sandbox, Agent, tool, AttestationLevel

# Create sandbox with tool execution tracking
sandbox = Sandbox.create(
    name="tool-demo",
    attestation=AttestationLevel.FULL,  # Include tool call proofs
)

# Define a verified tool
@tool(sandbox=sandbox, requires_approval=False)
def calculate(expression: str) -> float:
    """Safely evaluate a mathematical expression."""
    # Runs inside sandbox - no access to host filesystem
    return eval(expression, {"__builtins__": {}}, {})

# Create agent with the tool
agent = Agent(
    name="calculator",
    model="claude-sonnet-4-0",
    sandbox=sandbox,
    tools=[calculate],
)

# Run with tool use
result = agent.run("What is 1234 * 5678?")
print(result.output)

# Full attestation includes tool execution log
for call in result.attestation.tool_calls:
    print(f"Tool: {call.name}, Input: {call.input_hash}, Output: {call.output_hash}")
```

Run it:

```bash
python tool_example.py
```

---

## Step 4: Verify the Attestation (30 seconds)

Create `verify.py`:

```python
from oacp import verify_attestation

# Attestation from previous run
attestation_hash = "sha256:a1b2c3d4..."  # From result.attestation.hash

# Verify against OACP network (or local registry)
verification = verify_attestation(attestation_hash)

print(f"Valid: {verification.valid}")
print(f"Sandbox: {verification.sandbox_config}")
print(f"Executor: {verification.executor_version}")
print(f"Executed at: {verification.timestamp}")
```

---

## What You Learned

| Concept | What It Means |
|---------|---------------|
| **Sandbox** | Isolated execution environment (WASM-based) |
| **Attestation** | Cryptographic proof of what ran and what it produced |
| **Tool** | Function that executes inside sandbox with automatic verification |
| **Verification** | Third-party validation that attestation is genuine |

---

## Next Steps

1. **[Architecture Overview](./architecture.md)** — Understand how OACP works under the hood
2. **[API Reference](./api/README.md)** — Complete API documentation
3. **[Security Guide](./security/considerations.md)** — Production security requirements

---

## Quick Commands Reference

```bash
# Create a new project
oacp init my-project

# Run agent with attestation
oacp run agent.py --attest full

# Verify an attestation
oacp verify <attestation-hash>

# List active sandboxes
oacp sandbox list

# Stop a sandbox
oacp sandbox stop <sandbox-id>
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Sandbox creation failed` | Ensure Docker is running |
| `Attestation timeout` | Check network connection to OACP registry |
| `Tool not found` | Verify tool is registered with sandbox |
| `Verification failed` | Attestation may be expired (>24h) |

---

**You now have a working OACP-gated agent!** 🎉

For production deployments, see the [Security Considerations](./security/considerations.md) guide.
