# 🚀 Installation Guide

## Quick Install (60 seconds)

```bash
npx clawhub@latest install agentic-ai-gold
```

That's it. No dependencies. No configuration. It just works.

---

## Manual Install (If You Prefer)

### Step 1: Download

```bash
cd ~/clawd/skills  # or your skills directory
git clone https://github.com/dgclabs/agentic-ai-gold.git
```

### Step 2: Verify

```bash
cd agentic-ai-gold
python3 --version  # Should be 3.10+
clawhub doctor      # Verifies installation
```

### Step 3: Test

```bash
python3 examples/hello_agent.py
```

Expected output:
```
✓ Council activated
✓ 4-member council running
✓ 17 dharmic gates active
✓ Shakti Flow: ACTIVE
Agent ready.
```

---

## System Requirements

### Minimum
- Python 3.10+
- 4GB RAM
- 500MB disk space
- Internet connection

### Recommended
- Python 3.11+
- 8GB RAM
- 2GB disk space
- SSD storage

### Optional (For GPU Acceleration)
- CUDA-capable GPU
- 8GB+ VRAM
- PyTorch with CUDA

---

## First 5 Minutes

### Minute 1: Verify Installation
```bash
clawhub doctor
```
You should see: `✓ AGENTIC AI GOLD STANDARD installed correctly`

### Minute 2: Activate Council
```python
from agentic_ai import Council

council = Council()
council.activate()
print("Council running!")
```

### Minute 3: Check Status
```python
council.status()
```
Expected:
```
🧠 Gnata (Knower): ACTIVE
📚 Gneya (Known): ACTIVE  
⚡ Gnan (Knowing): ACTIVE
🔥 Shakti (Force): ACTIVE

17 Dharmic Gates: ALL ACTIVE
4-Tier Fallback: OPERATIONAL
Memory Systems: 5-LAYER ACTIVE
```

### Minute 4: Spawn Your First Specialist
```python
from agentic_ai import Specialist

researcher = Specialist.create(
    role="researcher",
    task="Summarize today's AI news",
    dharmic_gates=True
)

result = researcher.execute()
print(result)
```

### Minute 5: Enable Self-Improvement
```python
from agentic_ai import ShaktiFlow

flow = ShaktiFlow()
flow.enable_auto_evolution()

print("✓ Your skill will now improve itself overnight!")
```

---

## Troubleshooting

### Issue: `command not found: clawhub`

**Solution:**
```bash
# Install clawhub CLI
npm install -g clawhub

# Or use npx (no install needed)
npx clawhub@latest install agentic-ai-gold
```

### Issue: `ModuleNotFoundError: No module named 'agentic_ai'`

**Solution:**
```bash
# Ensure you're in the right directory
cd ~/clawd/skills/agentic-ai-gold

# Install dependencies
pip install -r requirements.txt

# Or use the included setup script
python3 setup.py
```

### Issue: `ImportError: cannot import name 'Council'`

**Solution:**
```bash
# Check Python version
python3 --version  # Must be 3.10+

# Try with explicit Python path
python3 -c "from agentic_ai import Council; print('OK')"
```

### Issue: API Key Errors

**Solution:**
```bash
# Set your OpenRouter key (for Tier 1 fallback)
export OPENROUTER_API_KEY=your_key_here

# Or add to ~/.bashrc or ~/.zshrc
echo 'export OPENROUTER_API_KEY=your_key_here' >> ~/.bashrc
```

### Issue: Slow Performance

**Solutions:**
1. **Enable Tier 4 (Local Only)** for offline work:
   ```python
   from agentic_ai import Config
   Config.set_fallback_tier(4)  # Uses local models only
   ```

2. **Reduce Council Size** for testing:
   ```python
   council = Council(minimal=True)  # 2 members instead of 4
   ```

3. **Disable Non-Essential Memory Layers**:
   ```python
   Config.memory_layers = ['working', 'semantic']  # Skip 3 layers
   ```

---

## Verification Checklist

After installation, verify everything works:

```bash
# Run the full verification suite
python3 -m agentic_ai.verify
```

Expected output:
```
✓ Core framework loaded
✓ 4-member council initialized
✓ 17 dharmic gates active
✓ 5-layer memory operational
✓ 4-tier fallback verified
✓ MCP protocol ready
✓ A2A protocol ready
✓ Self-improvement engine running
✓ Shakti Flow: ACTIVE

ALL SYSTEMS OPERATIONAL (16/17)
```

---

## Next Steps

### Read the Full Documentation
- [SKILL.md](SKILL.md) — Complete technical reference
- [PRICING.md](PRICING.md) — Features by tier

### Try Examples
```bash
ls examples/
# hello_agent.py       — Basic activation
# specialist_spawn.py  — Dynamic agent creation
# self_improvement.py  — Enable evolution
# memory_demo.py       — 5-layer memory demo
# security_gates.py    — See 17 gates in action
```

### Join the Community
- Discord: #agentic-ai-gold
- GitHub Discussions
- Email: support@dgclabs.ai

---

## Uninstallation

If you need to remove:

```bash
# Via clawhub
clawhub uninstall agentic-ai-gold

# Or manually
rm -rf ~/clawd/skills/agentic-ai-gold
```

Your data (memories, council state) is preserved in:
```
~/.agentic_ai/  # Can backup or delete separately
```

---

## Getting Help

Stuck? We're here:

1. **Check the FAQ** in [PRICING.md](PRICING.md)
2. **Search Discord** — someone probably had the same issue
3. **GitHub Issues** — bug reports and feature requests
4. **Email** — support@dgclabs.ai (48h response for Pro/Enterprise)

---

## Success! 🎉

You now have **AGENTIC AI GOLD STANDARD** installed.

Your agents will:
- ✅ Self-improve overnight
- ✅ Survive any API outage
- ✅ Remember everything (5 layers)
- ✅ Stay ethical (17 gates)
- ✅ Cost $0.05/day to run

**Welcome to the future of agentic AI.**

---

*Installation guide v4.0 • February 2026*
