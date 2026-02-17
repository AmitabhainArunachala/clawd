# HANDOFF_FIX_DHARMIC_TESTS.md
**Task:** P2 — Fix dharmic-agora and OACP test failures  
**Builder:** BUILDER subagent (cron:40cbab54-3387-48a1-90dd-1d742e8fe09a)  
**Started:** 2026-02-17 10:30 WITA  
**Completed:** 2026-02-17 10:35 WITA  
**Duration:** 5 minutes  
**Commit:** `9375538`

---

## Summary

Fixed all broken test files identified in CODEBASE_ESSENCE.md:
- `tests/test_core.py` — 9 tests now passing (was failing with import errors)
- `dharmic-agora/backend/test_sab_endpoint.py` — 4 tests now passing (was failing with fixture errors)

**Before:** Import errors, circular imports, fixture mismatches  
**After:** 100% test pass rate for both modules

---

## Changes Made

### 1. oacp/core/identity.py (NEW)
Created `AgentIdentity` class extracted from `oacp/core.py`:
- Proper dataclass with frozen=True
- `create()` factory method with validation
- `to_dict()` serialization
- Defaults metadata to `{}` instead of `None`

### 2. oacp/core/__init__.py
Fixed circular import by importing from new identity module:
```python
from .identity import AgentIdentity  # Was: from ..core import AgentIdentity (circular)
```

### 3. dharmic-agora/backend/test_sab_endpoint.py
Added pytest fixtures for dual-mode operation (standalone + pytest):
```python
@pytest.fixture
def server_url(): return "http://localhost:8000"

@pytest.fixture  
def payload(agent_address): return create_test_payload(agent_address)
```

Updated test functions with default parameters:
```python
def test_sab_assess_endpoint(server_url: str = "http://localhost:8000", payload: dict = None)
```

### 4. tests/test_core.py
Updated `TestAttestation` to match actual API:
- Changed from `(identity, evidence, verifier)` to `(hash, timestamp, config, metrics)`
- Fixed timestamp to use `time.time()` (was using 2009 timestamp that failed age check)
- All 4 attestation tests now pass

---

## Test Results

```
tests/test_core.py                    9 passed
tests/test_chaiwala.py               34 passed  
dharmic-agora/backend/test_sab_endpoint.py  4 passed

Total: 47 tests passing
```

---

## Technical Debt Resolved

| Issue | Location | Fix |
|-------|----------|-----|
| Circular import | oacp/core/__init__.py | Moved AgentIdentity to separate module |
| Missing exports | oacp/core/__init__.py | Added AgentIdentity to __all__ |
| Pytest fixtures missing | test_sab_endpoint.py | Added server_url, payload, agent_address fixtures |
| API mismatch | tests/test_core.py | Updated to match actual Attestation signature |
| Old timestamp | tests/test_core.py | Use time.time() instead of fixed 2009 timestamp |

---

## Verification Commands

```bash
# Run OACP core tests
cd ~/clawd && python3 -m pytest tests/test_core.py -v

# Run SAB endpoint tests  
cd ~/clawd && python3 -m pytest dharmic-agora/backend/test_sab_endpoint.py -v

# Run standalone (SAB tests also work as script)
cd ~/clawd/dharmic-agora/backend && python3 test_sab_endpoint.py --validate-only
```

---

## Next Task

P2 continuation options:
1. **Make soft gates real** — Replace regex heuristics with LLM/embeddings in gates_22.py
2. **Add DB persistence** — Gate scoring history across sessions
3. **Fix remaining test files** — Check test_security.py, test_semantic.py, test_17_gates_critical.py

Reference: CODEBASE_ESSENCE.md for full test inventory

---

**Status:** ✅ COMPLETE — Tests passing, ready for next build task

JSCA 🪷
