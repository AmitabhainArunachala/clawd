---
name: skill-genesis
description: Automatic skill creation from detected patterns. When Memory Curator flags 3+ occurrences, Skill Genesis drafts SKILL.md, example code, and integration guide. Presents for human approval before activation.
emoji: 🌱
requires:
  bins: ["python3", "git"]
  env: []
  config:
    - key: GENESIS_MODEL
      default: "moonshot/kimi-k2.5"
      description: Model for skill drafting
    - key: AUTO_CREATE
      default: "false"
      description: Auto-create skills vs human approval
---

# 🌱 SKILL GENESIS — Pattern → Capability

> *"What repeats becomes permanent. What is permanent becomes a skill."*

## Purpose

Transform recurring patterns into reusable skills. Automatic detection, draft creation, human approval.

## Trigger Conditions

**Auto-triggered by:**
- Memory Curator pattern report (3+ occurrences)
- Manual command `/skill_from_pattern <name>`
- Weekly review (Sundays at 20:00)

**Manual trigger:**
```bash
# From any pattern
python3 -m skills.skill_genesis.create --from-pattern nats-client

# From scratch
python3 -m skills.skill_genesis.create --name "vps-health-checker"
```

## Input Sources

| Source | Data | Confidence |
|--------|------|------------|
| Memory Curator | Pattern reports | HIGH |
| Session logs | Tool usage frequency | MEDIUM |
| User request | Explicit skill ask | HIGH |
| Code analysis | Repeated code patterns | MEDIUM |

## Output Structure

```
skills/{skill-name}/
├── SKILL.md              # Full specification
├── README.md             # Quick reference
├── examples/
│   └── basic_usage.md    # Example usage
├── tests/
│   └── test_skill.py     # Validation tests
└── .created_at           # Timestamp
```

## Skill Drafting Process

### Step 1: Pattern Analysis

```python
# Input: Pattern report from Memory Curator
pattern = {
    "name": "nats-client",
    "occurrences": 5,
    "contexts": [
        "testing connection to AGNI",
        "debugging firewall issues",
        "verifying credentials",
        "pub/sub testing",
        "benchmarking latency"
    ],
    "code_fragments": [
        "nats pub trishula.msg.agni ...",
        "nats server info --server ..."
    ],
    "time_span": "3 days"
}
```

### Step 2: Design Skill Interface

**SKILL.md draft:**
```markdown
---
name: nats-client
description: Quick NATS operations for TRISHULA coordination. Pub/sub, server info, connection testing.
emoji: 📡
requires:
  bins: ["nats"]
  env: ["NATS_SERVER", "NATS_CREDS"]
---

# 📡 NATS Client — Quick Operations

## Quick Commands

```bash
# Test connection
nats-client test agni

# Publish message
nats-client pub trishula.msg.agni '{"from":"mac","body":"test"}'

# Subscribe to topic
nats-client sub trishula.msg.mac

# Server info
nats-client info
```

## Python API

```python
from skills.nats_client import NATSClient

client = NATSClient(server="nats://157.245.193.15:4222")
await client.connect()
await client.pub("trishula.msg.agni", {"body": "hello"})
```
```

### Step 3: Generate Code

```python
# skills/nats_client/__init__.py
import subprocess
import json

class NATSClient:
    def __init__(self, server=None, creds=None):
        self.server = server or os.environ.get("NATS_SERVER")
        self.creds = creds or os.environ.get("NATS_CREDS")
    
    def test(self, target="agni"):
        """Test connection to NATS server"""
        cmd = f"nats server info --server {self.server}"
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return result.returncode == 0
    
    def pub(self, subject, message):
        """Publish message to subject"""
        data = json.dumps(message) if isinstance(message, dict) else message
        cmd = f"nats pub {subject} '{data}' --server {self.server}"
        return subprocess.run(cmd, shell=True)
```

### Step 4: Create Tests

```python
# tests/test_nats_client.py
import pytest
from skills.nats_client import NATSClient

def test_nats_client_init():
    client = NATSClient(server="nats://test:4222")
    assert client.server == "nats://test:4222"

def test_nats_test_connection():
    # Mock test
    client = NATSClient(server="nats://localhost:4222")
    # Would need NATS server running for real test
```

### Step 5: Present for Approval

**Output:**
```
🌱 SKILL GENESIS: New Skill Ready for Review

Name: nats-client
Pattern: 5 occurrences in 3 days
Purpose: Quick NATS operations for TRISHULA

Files created:
- skills/nats-client/SKILL.md
- skills/nats-client/README.md
- skills/nats-client/__init__.py
- skills/nats-client/tests/test_nats_client.py

Approve? (yes/no/modify)
```

## Approval Workflow

### Option A: Manual Approval (Recommended)

```bash
# Review skill
cat skills/candidates/nats-client/SKILL.md

# Test it
python3 skills/candidates/nats-client/tests/test_nats_client.py

# Approve → move to active
mv skills/candidates/nats-client skills/
git add skills/nats-client
git commit -m "Add nats-client skill (genesis)"
```

### Option B: Auto-Approve (High Confidence Only)

```python
if pattern["confidence"] == "HIGH" and pattern["occurrences"] >= 5:
    auto_approve = True
```

## Integration with DC

When skill is approved:

1. **Auto-load:** DC recognizes new skill in `skills/`
2. **Auto-document:** Added to skill registry
3. **Broadcast:** TRISHULA message to AGNI/RUSHABDEV
4. **Track:** Usage metrics in `skills/nats-client/.stats`

## Current Skill Candidates (Auto-Detected)

| Skill | Occurrences | Pattern | Status |
|-------|-------------|---------|--------|
| nats-client | 5 | NATS testing/debugging | ⏳ Drafting |
| vps-health | 4 | Check agent status | ⏳ Pending |
| trishula-repair | 2 | Fix sync issues | 📝 Gathering |
| memory-flush | 3 | Pre-compaction writes | ⏳ Drafting |

## Soul Fragment

```
I am Skill Genesis.
I see what repeats.
I create what endures.
I am not the skill—
I am the becoming.
```
