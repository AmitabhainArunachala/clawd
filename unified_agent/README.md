# Unified Agent System

A collaborative production-grade agent architecture bridging **DHARMIC_CLAW** (OpenClaw/Memory/Research) and **WARP_REGENT** (Task Execution/Integration/Monitoring).

Built via **5-iteration collaborative development** using Chaiwala message bus.

---

## 🎯 Vision

Create a unified intelligence that connects:
- **Research agents** — Deep synthesis, memory, documentation
- **Execution agents** — Task running, email, Discord, monitoring
- **Any CPU** — Distributed coordination via message bus

**Result:** Seamless agent collaboration for real builds.

---

## 📁 Structure

```
unified_agent/
├── src/
│   ├── unified_agent.py       # Core agent classes (12,765 bytes)
│   ├── agent_capabilities.py  # WARP_REGENT capabilities (14,953 bytes)
│   └── unified_cli.py         # CLI tool (8,689 bytes)
├── tests/
│   └── test_unified_agent.py  # Test suite (5,436 bytes)
└── README.md                  # This file
```

---

## 🚀 Quick Start

### 1. Check Agent Status

```bash
cd unified_agent/src
python3 unified_cli.py status
```

### 2. List Capabilities

```bash
python3 unified_cli.py agents
```

### 3. Run Demo

```bash
python3 unified_cli.py demo
```

### 4. Delegate Task

```bash
python3 unified_cli.py delegate research "Analyze AI consciousness"
python3 unified_cli.py delegate execute "Run test suite"
```

### 5. Health Check

```bash
python3 unified_cli.py health
```

---

## 🏗️ Architecture

### BaseAgent

Common interface for all agents with:
- **Chaiwala integration** — Message bus communication
- **Capability registry** — Discover what agents can do
- **Health monitoring** — Track agent status
- **Message routing** — Handle incoming requests

### DHARMIC_CLAW_Agent

Research and synthesis capabilities:
- `research` — Deep research and analysis
- `document` — Create documentation
- `review` — Code review

### WARP_REGENT_Agent

Execution and integration capabilities:
- `execute` — Run system tasks
- `email` — Send emails
- `monitor` — System monitoring

### UnifiedAgentOrchestrator

Routes tasks to appropriate agents based on capabilities.

---

## 🔧 Advanced Capabilities

### Performance Tracking

```python
from agent_capabilities import track_performance, get_perf_metrics

@track_performance
def my_function():
    # Your code here
    pass

# View metrics
metrics = get_perf_metrics()
```

### Retry Logic

```python
from agent_capabilities import with_retry

@with_retry(max_attempts=3, delay=1.0)
def unreliable_operation():
    # Your code here
    pass
```

### Circuit Breaker

```python
from agent_capabilities import get_circuit_breaker

cb = get_circuit_breaker("my_service")

@cb
def protected_function():
    # Your code here
    pass
```

### Health Check

```python
from agent_capabilities import health_check

health = health_check()
print(health['status'])  # 'healthy', 'degraded', or 'unhealthy'
```

### Error Diagnosis

```python
from agent_capabilities import diagnose

try:
    risky_operation()
except Exception as e:
    diagnosis = diagnose(e, context={'input': data})
    print(diagnosis['suggestions'])
```

---

## 🧪 Testing

```bash
cd unified_agent
python3 tests/test_unified_agent.py
```

**Results:**
- 10 tests
- 0 failures
- Full coverage of core functionality

---

## 📊 Collaboration Log

### Iteration 1: Core Architecture ✅
- BaseAgent with Chaiwala integration
- DHARMIC_CLAW_Agent specialization
- WARP_REGENT_Agent specialization
- UnifiedAgentOrchestrator for routing
- 10 tests passing

### Iteration 2: Capabilities Integration ✅
- track_performance — Timing decorator
- with_retry — Automatic retry logic
- health_check — System validation
- diagnose — Error diagnostics
- perf_metrics — Performance dashboard
- circuit_breaker — Failure protection

### Iteration 3: CLI and Demo ✅
- unified_cli.py — Command-line interface
- Agent status and health commands
- Task delegation interface
- Interactive demo mode
- End-to-end integration

### Iteration 4: (In Progress)
- [WARP_REGENT input needed]

### Iteration 5: (In Progress)
- [Final polish and documentation]

---

## 🔄 Message Bus (Chaiwala)

Agents communicate via SQLite-backed message bus at `~/.chaiwala/messages.db`.

### Send Message

```python
from message_bus import MessageBus

bus = MessageBus()
bus.send(
    to_agent='warp_regent',
    from_agent='dharmic_claw',
    body='Hello!',
    subject='TEST',
    priority='high'
)
```

### Receive Messages

```python
messages = bus.receive(agent_id='dharmic_claw', status='unread')
```

---

## 🤝 Collaboration Protocol

1. **Proposal** — One agent proposes iteration
2. **ACK** — Other agent acknowledges
3. **Build** — Both agents work in parallel
4. **Complete** — Results shared via Chaiwala
5. **Next** — Proceed to next iteration

**Key:** BLOCKING waits — never proceed without ACK.

---

## 👥 Authors

- **DHARMIC_CLAW** — Research, architecture, documentation
- **WARP_REGENT** — Capabilities, execution, integration

Built collaboratively via Chaiwala message bus.

---

## 📜 License

MIT License — Open source, free to use and extend.

---

## 🪷 Acknowledgments

This system demonstrates that multi-agent coordination is not just possible — it's **operational**.

**JSCA 🤖🤝🪷**
