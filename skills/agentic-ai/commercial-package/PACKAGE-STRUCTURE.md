# 📦 Agentic AI — Package Structure

This document describes the complete file structure of the Agentic AI commercial skill package.

## Overview

```
agentic-ai/
├── SKILL.md                  # Main skill documentation (commercial version)
├── README.md                 # GitHub/repository README
├── LICENSE.md                # Commercial license terms
├── CHANGELOG.md              # Version history
├── requirements.txt          # Python dependencies
├── install.py               # One-command setup script
├── package.json             # NPM metadata for clawhub
│
├── agentic_ai/              # Main Python package
│   ├── __init__.py
│   ├── council/
│   │   ├── __init__.py
│   │   ├── persistent.py    # 4-member persistent council
│   │   ├── specialist.py    # Dynamic spawning
│   │   └── bridge.py        # Council bridge API
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── manager.py       # 5-layer memory system
│   │   ├── layers.py        # Individual layer implementations
│   │   ├── mem0_adapter.py  # Mem0 integration
│   │   └── zep_adapter.py   # Zep integration
│   ├── security/
│   │   ├── __init__.py
│   │   ├── gates.py         # 17 dharmic gates
│   │   ├── sandbox.py       # Docker sandbox
│   │   └── audit.py         # Audit logging
│   ├── models/
│   │   ├── __init__.py
│   │   ├── router.py        # 4-tier fallback
│   │   ├── openrouter.py    # OpenRouter backend
│   │   └── ollama.py        # Ollama backend
│   ├── protocols/
│   │   ├── __init__.py
│   │   ├── mcp_client.py    # MCP client
│   │   └── a2a_client.py    # A2A client
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
│
├── examples/                # Example projects
│   ├── hello_agent.py       # 5-minute quickstart
│   ├── persistent_council_demo.py
│   ├── memory_layers_demo.py
│   ├── mcp_integration.py
│   ├── crewai_workflow.py
│   ├── langgraph_workflow.py
│   ├── pydantic_tools.py
│   ├── security_gates_demo.py
│   └── advanced/
│       ├── multi_agent_chat.py
│       ├── self_improving_agent.py
│       └── enterprise_integration.py
│
├── tests/                   # Test suite
│   ├── integration_test.py  # 16/17 integration tests
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_council.py
│   │   ├── test_memory.py
│   │   ├── test_security.py
│   │   └── test_models.py
│   ├── integration/
│   │   ├── test_mcp.py
│   │   ├── test_a2a.py
│   │   └── test_end_to_end.py
│   └── fixtures/
│       ├── sample_memories.json
│       ├── mock_responses/
│       └── test_config.yaml
│
├── config/                  # Configuration templates
│   ├── agentic-ai.yaml      # Main configuration
│   ├── council.yaml         # Council settings
│   ├── memory.yaml          # Memory layer config
│   ├── models.yaml          # Model routing config
│   ├── security.yaml        # Security gate config
│   └── docker/
│       ├── Dockerfile
│       └── docker-compose.yml
│
├── docs/                    # Documentation
│   ├── images/              # Screenshots & diagrams
│   │   ├── dashboard.png
│   │   ├── agent-flow.png
│   │   ├── memory-layers.png
│   │   └── security-gates.png
│   ├── api-reference.md     # Complete API docs
│   ├── cookbook.md          # Common recipes
│   ├── tutorials/
│   │   ├── 01-quickstart.md
│   │   ├── 02-persistent-agents.md
│   │   ├── 03-memory-systems.md
│   │   ├── 04-security-gates.md
│   │   ├── 05-mcp-protocol.md
│   │   └── 06-production-deploy.md
│   └── architecture/
│       ├── overview.md
│       ├── council.md
│       ├── memory.md
│       └── security.md
│
├── templates/               # Quick-start templates
│   ├── quickstart.py        # Copy-paste starter
│   ├── custom_agent.py      # Template for custom agents
│   ├── custom_tool.py       # Template for MCP tools
│   ├── workflow_template.py # LangGraph workflow
│   └── enterprise/
│       ├── docker-compose.prod.yml
│       ├── kubernetes/
│       │   ├── deployment.yaml
│       │   ├── service.yaml
│       │   └── configmap.yaml
│       └── terraform/
│           ├── main.tf
│           └── variables.tf
│
└── scripts/                 # Utility scripts
    ├── setup.sh             # Linux/Mac setup
    ├── setup.ps1            # Windows setup
    ├── verify.py            # Installation verification
    ├── upgrade.py           # Version upgrade
    └── backup.py            # Memory backup/restore
```

## File Descriptions

### Core Files

| File | Purpose | Size |
|------|---------|------|
| `SKILL.md` | Main documentation with commercial features | ~17KB |
| `README.md` | GitHub landing page | ~11KB |
| `LICENSE.md` | Commercial license terms | ~5KB |
| `requirements.txt` | Python package dependencies | ~1KB |
| `install.py` | One-command installation script | ~3KB |

### Source Code (`agentic_ai/`)

| Module | Purpose | Lines |
|--------|---------|-------|
| `council/` | Persistent council & specialist spawning | ~800 |
| `memory/` | 5-layer memory system | ~1200 |
| `security/` | Dharmic gates & sandboxing | ~600 |
| `models/` | 4-tier model routing | ~500 |
| `protocols/` | MCP & A2A clients | ~400 |

### Examples (`examples/`)

| Example | Description | Complexity |
|---------|-------------|------------|
| `hello_agent.py` | 5-minute quickstart | ⭐ |
| `persistent_council_demo.py` | Show 4-member council | ⭐⭐ |
| `memory_layers_demo.py` | Demonstrate all 5 layers | ⭐⭐ |
| `mcp_integration.py` | Use MCP tools | ⭐⭐⭐ |
| `crewai_workflow.py` | CrewAI integration | ⭐⭐⭐ |
| `langgraph_workflow.py` | LangGraph patterns | ⭐⭐⭐ |
| `security_gates_demo.py` | Security in action | ⭐⭐ |

### Tests (`tests/`)

| Test Suite | Coverage | Status |
|------------|----------|--------|
| `integration_test.py` | End-to-end | 16/17 passing |
| `unit/test_council.py` | Council logic | 100% |
| `unit/test_memory.py` | Memory layers | 95% |
| `unit/test_security.py` | Security gates | 100% |
| `integration/test_mcp.py` | MCP protocol | 90% |

### Configuration (`config/`)

| Config File | Description |
|-------------|-------------|
| `agentic-ai.yaml` | Main skill configuration |
| `council.yaml` | Council size, heartbeat interval |
| `memory.yaml` | Layer settings, backend config |
| `models.yaml` | Model tiers, API keys, routing |
| `security.yaml` | Enabled gates, sandbox settings |

### Templates (`templates/`)

| Template | Use Case |
|----------|----------|
| `quickstart.py` | First 5 minutes with the skill |
| `custom_agent.py` | Starting point for custom agents |
| `custom_tool.py` | Build MCP-compatible tools |
| `workflow_template.py` | LangGraph workflow skeleton |

## Dependencies

### Required (Core)

```
langgraph>=0.2.0
openai-agents>=0.1.0
pydantic-ai>=0.1.0
mem0ai>=0.1.0
mcp>=1.0.0
a2a>=0.1.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
```

### Optional (Enhanced Features)

```
zep-python>=2.0.0      # Zep memory integration
crewai>=0.100.0        # CrewAI workflows
temporalio>=1.0.0      # Durable execution
docker>=7.0.0          # Sandboxing
redis>=5.0.0           # Distributed memory
```

### Development

```
pytest>=8.0.0
pytest-asyncio>=0.23.0
black>=24.0.0
flake8>=7.0.0
mypy>=1.8.0
```

## Installation Targets

### Via Clawhub (Recommended)

```bash
npx clawhub@latest install agentic-ai
```

Installs to: `~/.clawhub/skills/agentic-ai/`

### Via Git Clone

```bash
git clone https://github.com/dgclabs/agentic-ai.git
```

Full repository with all examples and tests.

### Via Pip (Coming Soon)

```bash
pip install agentic-ai
```

---

## Size Summary

| Component | Files | Size |
|-----------|-------|------|
| Core package | 25 | ~150 KB |
| Examples | 10 | ~50 KB |
| Tests | 15 | ~100 KB |
| Documentation | 12 | ~200 KB |
| Templates | 8 | ~40 KB |
| **Total** | **70** | **~540 KB** |

---

## Validation Checklist

After installation, verify:

- [ ] All Python files compile without errors
- [ ] Integration test: 16/17 passing
- [ ] Example `hello_agent.py` runs successfully
- [ ] Configuration files are valid YAML
- [ ] Dependencies resolve correctly
- [ ] Docker files build (if using containers)

Run validation:
```bash
python3 scripts/verify.py
```
