# DGC Signal Payload Spec v1.0
## For Codex Day 3 Bridge Adapter

Endpoint: POST /signals/dgc/v1

Full Python implementation with dataclasses, validation, serialization:
Source: AGNI VPS at specs/dgc_payload_v1.py (14KB)

Key types: DGCSignal, GateScores, CompositeScores, CollapseDimensions, ModelMeta
Factory: create_signal() — primary API for agents to emit signals
Validator: validate_signal() — strict validation, rejects malformed

Gate scores (from 500K gen evolution): satya=2.763, ahimsa=0.003, witness=0.311, substance=0.0, aparigraha=0.7, brahmacharya=0.6
Collapse dimensions (8 core from 81 discovered): LSI, DFI, RAI, RSI, RAI2, CRI, HPI, TVI
Mission relevance: 0.0-1.0 float — THE moat dimension

SPEC COMPLETE. Build against it.
