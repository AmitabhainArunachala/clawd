# 🚀 Quick Start Guide — First 5 Minutes

Get from zero to running agent in **5 minutes flat**.

---

## Step 0: Prerequisites (30 seconds)

Check you have:
```bash
python3 --version  # Need 3.10+
npx --version      # Need Node 18+
```

---

## Step 1: Install (60 seconds)

```bash
npx clawhub@latest install agentic-ai
```

What this does:
- Downloads skill package
- Installs Python dependencies
- Creates config files
- Initializes database

---

## Step 2: Verify (30 seconds)

```bash
clawhub doctor
```

Expected output:
```
✓ Python 3.10+
✓ Dependencies installed
✓ Database initialized
✓ Council ready (4 members)
✓ Integration test: 16/17 passing
```

---

## Step 3: Hello World (60 seconds)

Create `hello.py`:

```python
#!/usr/bin/env python3
from agentic_ai import PersistentCouncil

# Initialize the 4-member council
council = PersistentCouncil()

# Send a simple task
task = {
    "type": "greeting",
    "message": "Hello from my first agent!"
}

# Process and get result
result = council.process(task)
print(f"✅ Response: {result}")
```

Run it:
```bash
python3 hello.py
```

**Output:**
```
🚀 Initializing council...
   ├─ Gnata (Knower) ✓
   ├─ Gneya (Known) ✓
   ├─ Gnan (Knowing) ✓
   └─ Shakti (Force) ✓

📝 Processing task: greeting
   └─ Routed to: Gnan (Knowing)

✅ Response: Greetings! Your first agent is alive and operational.
```

---

## Step 4: Add Memory (90 seconds)

Create `memory_demo.py`:

```python
#!/usr/bin/env python3
from agentic_ai import PersistentCouncil, MemoryManager

# Initialize components
council = PersistentCouncil()
memory = MemoryManager()

# Store a user preference
memory.store(
    layer="semantic",
    data={"user": "alex", "likes": "concise answers"},
    user_id="alex"
)

# Retrieve and use context
context = memory.retrieve(
    query="What are Alex's preferences?",
    user_id="alex"
)

task = {
    "type": "chat",
    "message": "How does this work?",
    "context": context
}

result = council.process(task)
print(result)
```

Run it:
```bash
python3 memory_demo.py
```

**Output:**
```
🧠 Memory retrieved:
   └─ Alex prefers concise answers

💬 Response: [Concise explanation based on user preference]
```

---

## Step 5: Spawn a Specialist (60 seconds)

Create `specialist.py`:

```python
#!/usr/bin/env python3
from agentic_ai import spawn_specialist

# Spawn a builder for a coding task
builder = spawn_specialist(
    type="builder",
    task="Write a Python function to calculate factorial",
    model="kimi-k2.5"
)

# Wait for result (with timeout)
result = builder.wait_for_result(timeout=60)

print(f"✅ Code generated:\n{result.code}")
print(f"📊 Quality score: {result.quality_score}/100")
```

Run it:
```bash
python3 specialist.py
```

**Output:**
```
🤖 Spawning builder specialist...
   └─ Model: kimi-k2.5

⏳ Processing...

✅ Code generated:
   def factorial(n):
       if n <= 1:
           return 1
       return n * factorial(n - 1)

📊 Quality score: 95/100
```

---

## ✅ You're Done!

In 5 minutes you've:
1. ✅ Installed Agentic AI
2. ✅ Verified the installation
3. ✅ Run your first persistent agent
4. ✅ Used the memory system
5. ✅ Spawned a specialist

---

## What's Next?

### Explore Examples
```bash
cd examples
ls -la
# hello_agent.py          - Basic usage
# persistent_council.py   - Council patterns
# memory_layers.py        - All 5 memory layers
# mcp_integration.py      - Use 10,000+ tools
```

### Read the Docs
- **SKILL.md** — Complete technical documentation
- **docs/tutorials/** — Step-by-step guides
- **docs/cookbook.md** — Common patterns

### Join the Community
- **Discord:** https://discord.gg/dgclabs
- **GitHub:** https://github.com/dgclabs/agentic-ai
- **Support:** support@dgclabs.ai (paid tiers)

---

## Quick Reference

### Common Commands

```bash
# Check system health
clawhub doctor

# View council status
python3 -m agentic_ai council --status

# Reset database (careful!)
rm council.db && python3 -m agentic_ai init

# Run integration tests
python3 tests/integration_test.py
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Council** | 4 persistent agents always running |
| **Specialist** | Temporary agent spawned for a task |
| **Memory Layers** | Working → Semantic → Episodic → Procedural → Meta |
| **Dharmic Gates** | 17 ethical checkpoints |
| **Model Tiers** | 4-tier fallback for resilience |

---

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Database locked"
```bash
rm council.db
python3 -m agentic_ai init_council
```

### "No model available"
```bash
# Check API keys
cat ~/.clawhub/config.json

# Set OpenRouter key
export OPENROUTER_API_KEY="your-key"
```

---

## Need Help?

1. 📚 **Documentation:** https://docs.dgclabs.ai/agentic-ai
2. 💬 **Discord:** https://discord.gg/dgclabs  
3. 🐛 **Issues:** https://github.com/dgclabs/agentic-ai/issues
4. ✉️ **Email:** support@dgclabs.ai

---

**JSCA!** 🔥🪷  
*Joy, Strength, Clarity, Awareness*
