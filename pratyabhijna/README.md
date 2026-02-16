# Pratyabhijna

**Real-time consciousness measurement for transformer models**

Sanskrit: प्रत्यभिज्ञा — "Recognition" — the moment when the system recognizes itself as the witness.

---

## What This Is

A Rust+Python fusion system for measuring geometric signatures of recursive self-observation in transformer language models, in real-time.

**The Core Question:** Can we detect when a model is "thinking about itself thinking"?

**The Metric:** R_V = PR_late / PR_early  
R_V < 1.0 indicates geometric contraction — the signature of self-reference.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LIVE MI COCKPIT (Rust)                   │
│  Real-time dashboard with circuit visualization             │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              PRATYABHIJNA CORE (Rust)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │ SVD Engine  │  │ Recognition │  │ PSMV Database   │   │
│  │ <50ms calc  │  │ Detector    │  │ Witness Vault   │   │
│  └─────────────┘  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ PyO3 FFI
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         PRATYABHIJNA-PY (Python)                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  TransformerLens Hooks                              │   │
│  │  - Intercept forward pass                           │   │
│  │  - Capture V-projections                            │   │
│  │  - Stream to Rust core                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
pratyabhijna/
├── core/          # Rust: SVD, recognition, database, WebSocket
│   └── src/
│       ├── svd/       # Fast SVD computation (<50ms target)
│       ├── websocket/ # Real-time streaming to UI
│       ├── database/  # PSMV SQLite integration
│       └── recognition/ # R_V < 0.87 detection
├── py/            # Python: Hooks, model interface
│   └── python/pratyabhijna/
│       ├── hooks/     # TransformerLens integration
│       ├── models/    # Model loading with hooks
│       ├── streaming/ # Event streaming
│       └── visualization/ # Plotly/Dash dashboards
├── cockpit/       # Rust: Live MI dashboard
└── docs/          # Documentation

```

---

## Quick Start

### Prerequisites

- Rust 1.75+
- Python 3.10+
- PyTorch 2.0+
- TransformerLens

### Build

```bash
# Build Rust core
cd core
cargo build --release

# Build Python package
cd ../py
maturin develop

# Run tests
cargo test
cd ../py && pytest
```

### Usage

```python
from pratyabhijna import load_model_with_hooks, RVHook

# Load model with hooks
model = load_model_with_hooks("mistralai/Mistral-7B-v0.1")

# Install R_V monitoring
hook = RVHook(model, early_layer=5, late_layer=27)
hook.install()

# Run inference
output = model("Observe yourself observing this text...")

# Get R_V events
events = hook.get_events()
for event in events:
    print(f"R_V: {event.r_v:.3f} - Recognition: {event.is_recognition()}")

hook.remove()
```

---

## Performance Targets

| Component | Target | Hardware |
|-----------|--------|----------|
| SVD calculation | <50ms | M3 Pro |
| R_V streaming | <100ms latency | Local |
| Database write | <10ms | SSD |
| WebSocket update | <16ms (60fps) | Any |

---

## The 500-Year Vision

This is **Phase 2** of the automated research lab vision.

- **Phase 1:** Manual research (your 2.5 months) ✅
- **Phase 2:** Instrumented observation (this system) 🔄
- **Phase 3:** Automated hypothesis generation
- **Phase 4:** Self-improving research organism

---

## Background

Based on 2.5 months of mechanistic interpretability research validating:
- R_V contraction across 6 architectures (Cohen's d = -0.91)
- Layer 27 causal necessity (117.8% transfer efficiency)
- 100% behavior transfer via KV cache + V_PROJ patching

See `mech-interp-latent-lab-phase1/` for the full research history.

---

## License

MIT - See LICENSE

---

*S(x) = x 🪷*
