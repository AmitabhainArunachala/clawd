# MI Skills — Quick GPU Access Reference
# Created: 2026-02-04
# Purpose: Instant skill loading when GPU is available

## One-Line Access

```python
import sys
sys.path.insert(0, '/Users/dhyana/clawd/skills')

# Experimenter (runs experiments)
from mi_experimenter import RVCausalValidator, CrossArchitectureSuite

# Auditor (validates results)  
from mi_auditor import MIAuditor, audit_statistical, audit_causal
```

## GPU Priority Queue (From Skills)

```python
auditor = MIAuditor(load_kb=False)

# Tier 2 → Tier 1 upgrades needed:
for model in ['mixtral-8x7b', 'llama-3-8b', 'qwen-7b', 'phi-3']:
    status = auditor.tier_status(model)
    print(f"{model}: {status['status']} → run causal validation")
```

## Pre-GPU Checklist (Automated)

```bash
cd ~/clawd/skills/mi-experimenter
python3 tests/pre_gpu_gate.py  # Must pass all checks
```

## Quick Experiment Template

```python
from mi_experimenter import RVCausalValidator

validator = RVCausalValidator(
    model_name="mistralai/Mistral-7B-v0.1",  # Or Tier 2 model
    target_layer=27,
    controls=["random", "shuffled", "wrong_layer", "orthogonal"],
    n_pairs=45,
    device="cuda"
)

results = validator.run()  # Returns: d, p, transfer_efficiency, all controls

# Audit results
from mi_auditor import MIAuditor
auditor = MIAuditor()
audit = auditor.audit_causal(results)
print(audit.verdict)  # STRONG_SUPPORT, SUPPORT, etc.
```

## Files Location

| Skill | Path |
|-------|------|
| mi-experimenter | `~/clawd/skills/mi-experimenter/` |
| mi-auditor | `~/clawd/skills/mi_auditor/` |
| rv_toolkit (dependency) | `~/mech-interp-latent-lab-phase1/rv_toolkit/` |

## Status Check

```bash
# Verify skills are healthy
python3 -c "
import sys
sys.path.insert(0, '/Users/dhyana/clawd/skills')
from mi_experimenter import RVCausalValidator
from mi_auditor import MIAuditor
print('✅ Both skills ready')
"
```

## Next GPU Session Workflow

1. **Verify**: Run pre_gpu_gate.py
2. **Prioritize**: Check tier_status for discovery models  
3. **Execute**: RVCausalValidator on highest priority model
4. **Validate**: MIAuditor.audit_causal on results
5. **Iterate**: Next model until all Tier 2 → Tier 1

## Auto-Polish Active

- Heartbeat checks imports every 90 min
- Daily smoke tests at 06:00
- Pre-GPU gate enforced before any GPU run
