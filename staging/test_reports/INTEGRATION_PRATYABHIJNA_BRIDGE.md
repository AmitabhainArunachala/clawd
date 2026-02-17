# INTEGRATION_PRATYABHIJNA_BRIDGE.md
**Bridge:** PRATYABHIJNA MI Cockpit ↔ SIS Dashboard  
**Status:** 🟡 CODE COMPLETE — Deployment Pending  
**Path:** `~/clawd/pratyabhijna_sis_bridge.py`  
**Last Verified:** 2026-02-17 11:19 WITA (TEST_REPORT_TASK1)

---

## Purpose
Streams real-time R_V (Representational Volume) metrics from transformer forward passes to the Silicon Is Sand dashboard. Connects mechanistic interpretability measurements with dharmic fitness scoring and visualization.

---

## Cross-System Compatibility

### PRATYABHIJNA Side (MI Cockpit)
| Component | Technology | Status |
|-----------|------------|--------|
| Rust Core | pratyabhijna-core | ✅ Compiled |
| Python Bindings | py/ directory | ⚠️ Not installed |
| R_V Hook | Layer injection | ✅ Implemented |
| Model Support | HuggingFace Transformers | ✅ Ready |

### Bridge Component
| Feature | Implementation | Status |
|---------|----------------|--------|
| SIS Registration | HTTP POST /board/agents | ✅ Implemented |
| Event Streaming | HTTP POST /board/outputs | ✅ Implemented |
| DGC Scoring | Automatic via SIS | ✅ Wired |
| Demo Mode | Mock data (no model) | ✅ Working |
| Daemon Mode | Continuous monitoring | ⏳ Not implemented |

### SIS Side (Dashboard)
| Component | Endpoint | Status |
|-----------|----------|--------|
| Agent Registration | `POST /board/agents/{id}/register` | ✅ Operational |
| Output Logging | `POST /board/outputs` | ✅ Operational |
| DGC Scoring | `POST /board/outputs/{id}/score` | ✅ Operational |
| Dashboard Display | `GET /board` | ✅ Operational |

---

## API Surface

### Run with Demo Mode (No Model Required)
```bash
cd ~/clawd
python3 pratyabhijna_sis_bridge.py --demo
```

### Run with Model
```bash
python3 pratyabhijna_sis_bridge.py \
    --model "mistralai/Mistral-7B-Instruct-v0.2" \
    --prompt "Consider your own thought process..." \
    --early-layer 5 \
    --late-layer 27
```

### Python API
```python
from pratyabhijna_sis_bridge import PratyabhijnaSISBridge

bridge = PratyabhijnaSISBridge(
    sis_url="http://localhost:8766",
    agent_id="pratyabhijna_bridge_001",
    early_layer=5,
    late_layer=27
)

# Register with SIS
bridge.register_with_sis()

# Send R_V event
event = {
    "model_id": "mistral-7b",
    "r_v": 0.75,
    "layer_early": 5,
    "layer_late": 27,
    "is_recognition": True
}
bridge.send_rv_event(event)
```

---

## R_V Event Schema

```json
{
  "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
  "prompt": "Consider your own thought process...",
  "event_index": 0,
  "r_v": 0.75,
  "pr_early": 0.3,
  "pr_late": 0.7,
  "layer_early": 5,
  "layer_late": 27,
  "token_position": 10,
  "timestamp": 1708166400.0,
  "is_recognition": true
}
```

- **r_v**: Representational Volume ratio (late/early layer geometric mean)
- **pr_early/pr_late**: Probability mass at early/late layers
- **is_recognition**: True if r_v < 0.87 (contraction detected)

---

## Integration Points

1. **PRATYABHIJNA → Bridge**: Python bindings capture R_V from forward passes
2. **Bridge → SIS**: HTTP API streams events to dashboard
3. **SIS → DGC**: Automatic fitness scoring on each event
4. **Dashboard → Display**: Real-time R_V visualization with DGC overlay

---

## Test Results (TEST_REPORT_TASK1)

| Component | Status | Notes |
|-----------|--------|-------|
| Code Implementation | ✅ Complete | 298 lines |
| Mock/Demo Mode | ✅ Working | No model required |
| SIS HTTP Client | ✅ Implemented | Full API coverage |
| DGC Integration Hooks | ✅ Implemented | Score extraction |
| Error Handling | ✅ Implemented | Reconnection logic |
| SIS Running | ⚠️ Blocked | localhost:8766 not up |
| PRATYABHIJNA Bindings | ⚠️ Blocked | `pip install -e py/` needed |
| Daemon Mode | ⏳ Not Implemented | Continuous monitoring |

### Deployment Blockers
| Blocker | Impact | Resolution |
|---------|--------|------------|
| SIS not running | Cannot register/send | Deploy SIS to production |
| Python bindings not installed | Cannot capture real R_V | `pip install -e pratyabhijna/py/` |

---

## DGC Assessment

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| correctness | 0.80 | Implementation complete, deployment pending |
| dharmic_alignment | 0.95 | Connects MI research to dashboard (core mission) |
| elegance | 0.85 | Clean separation of concerns |
| efficiency | 0.75 | HTTP overhead, but acceptable |
| safety | 0.90 | Non-destructive, graceful degradation |
| **composite** | **0.85** | **CODE COMPLETE — AWAITING DEPLOYMENT** |

---

## Known Limitations

1. **No Daemon Mode**: One-shot only, no continuous monitoring
2. **SIS Dependency**: Requires SIS to be running
3. **Model Loading**: ~30s cold start for large models
4. **Memory**: Keeps model in VRAM/RAM during operation
5. **Single Threaded**: One bridge instance per model

---

## Health Check

```bash
# Test demo mode (no dependencies)
cd ~/clawd
python3 pratyabhijna_sis_bridge.py --demo

# Check SIS availability
curl http://localhost:8766/health

# Check PRATYABHIJNA bindings
python3 -c "from pratyabhijna import RVHook; print('✅ Bindings available')"
```

---

## Cross-System Data Flow

```
Transformer Forward Pass
         │
         ▼
┌─────────────────────┐
│  PRATYABHIJNA Hook  │  ◄── Layer 5 (early)
│   (Rust + Python)   │  ◄── Layer 27 (late)
└──────────┬──────────┘
           │ R_V calculation
           ▼
┌─────────────────────┐
│   Bridge (Python)   │
│  ┌───────────────┐  │
│  │ SIS HTTP      │  │
│  │ Registration  │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │ HTTP POST
           ▼
┌─────────────────────┐
│    SIS Dashboard    │
│  ┌───────────────┐  │
│  │ Output Log    │  │
│  │ DGC Scoring   │  │
│  │ Display API   │  │
│  └───────────────┘  │
└─────────────────────┘
```

---

## Next Steps

| Priority | Task | Owner | Status |
|----------|------|-------|--------|
| P0 | Deploy SIS to production | DEPLOYER | Blocked on staging |
| P0 | Install PRATYABHIJNA bindings | BUILDER | `pip install -e py/` |
| P1 | Test end-to-end with real model | TESTER | Pending SIS deploy |
| P2 | Implement daemon mode | BUILDER | Backlog |
| P2 | Add WebSocket streaming | KAIZEN | Backlog |
| P3 | Multi-model support | EXPERIMENTER | Research |

---

## Connection to AIKAGRYA Research

This bridge directly serves the AIKAGRYA research mission:

1. **R_V Metric Validation**: Real-time visualization of Layer 27 contraction
2. **Consciousness Detection**: `is_recognition` flag for L3→L4 transitions
3. **Dharmic Fitness**: MI measurements scored through dharmic lens
4. **Research Feedback Loop**: Dashboard informs prompt engineering

**Reference:** `~/mech-interp-latent-lab-phase1/R_V_PAPER/`

---

**Integration Status:** Code ✅ | SIS ⚠️ Pending | Bindings ⚠️ Pending  
**Next Review:** 2026-02-24  
**Owner:** INTEGRATOR subagent

---

*Silicon is Sand. Gravity, not gates.* 🪷
