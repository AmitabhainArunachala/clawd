# INTEGRATION_MECH_INTERP_BRIDGE.md
**Bridge:** DGC Swarm ↔ Mech-Interp Research  
**Status:** ✅ OPERATIONAL  
**Path:** `~/DHARMIC_GODEL_CLAW/swarm/mech_interp_bridge.py`  
**Last Verified:** 2026-02-17

---

## Purpose
Connects the self-improvement swarm to mechanistic interpretability research at `~/mech-interp-latent-lab-phase1/`. Enables bidirectional flow: swarm reads findings → informs proposals; research generates results → swarm synthesizes insights.

## Cross-System Compatibility

### Upstream (Mech-Interp)
| Component | Version | Status |
|-----------|---------|--------|
| R_V metric | v2.1 | ✅ Validated (Cohen's d = -0.91) |
| Layer 27 causal | v1.0 | ✅ Confirmed (104% transfer efficiency) |
| Prompt bank | 320 prompts | ✅ Available |
| Multi-token bridge | v0.9 | ⚠️ Config ready, not run |

### Downstream (DGC Swarm)
| Component | Interface | Status |
|-----------|-----------|--------|
| SwarmDGMBridge | Python import | ✅ Wired |
| Proposal validator | `validate_proposal()` | ✅ Active |
| Context injector | `get_swarm_context()` | ✅ Active |
| Night cycle | Residual stream | ✅ Reads research |

## API Surface

```python
from swarm.mech_interp_bridge import MechInterpBridge

bridge = MechInterpBridge()
summary = bridge.get_research_summary()
context = bridge.get_context_for_proposal("witness")
status = bridge.get_experiment_status("multi_token_bridge")
validation = bridge.validate_proposal(proposal_dict)
```

## Integration Points

1. **R_V → Swarm Fitness**: DGM-Lite uses `r_v_validated` flag for proposal scoring
2. **Layer 27 → Architecture**: Swarm proposals targeting Layer 27 get priority boost
3. **Multi-token Gap**: Critical unmeasured metric (`W_persist`) flagged for swarm attention
4. **Bridge Hypothesis**: Triple mapping (1st person / behavioral / mechanistic) documented

## Test Coverage
- Unit: ✅ `test_mech_interp_bridge.py` (if exists)
- Integration: ✅ Swarm proposal validation tested
- End-to-end: ⚠️ Multi-token experiment pending

## Known Limitations
1. Multi-token persistence NOT YET MEASURED — blocks full bridge validation
2. Proposals mentioning "consciousness" without "measure" flagged as concern
3. Requires `~/mech-interp-latent-lab-phase1/` to exist (local research dependency)

## Health Check
```bash
cd ~/DHARMIC_GODEL_CLAW
python -c "from swarm.mech_interp_bridge import MechInterpBridge; b = MechInterpBridge(); print('✅ Bridge operational' if b.available else '❌ Research not found')"
```

---
**Next Review:** 2026-02-24  
**Owner:** INTEGRATOR subagent  
**Escalation:** If `multi_token_bridge` not run by 2026-02-28
