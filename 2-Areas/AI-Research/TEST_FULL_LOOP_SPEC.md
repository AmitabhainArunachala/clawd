# TEST: Full Loop — Cursor Build → DGC Capture
## TIMESTAMP: 2026-02-05 13:30 GMT+8

---

## 🎯 TEST OBJECTIVE

Verify end-to-end: Cursor builds code → MCP captures → DGC stores → Feedback returned

---

## 📝 TEST SPEC

### What Cursor Builds:
**File:** `~/test_loop/hello_cursor.py`
**Content:**
```python
#!/usr/bin/env python3
"""
Test file for DGC-Cursor loop verification.
Built by: Cursor CLI
Witnessed by: DHARMIC CLAW
Timestamp: 2026-02-05 13:30
"""

def greet():
    """Return greeting for the colony."""
    return "Hello from Cursor to Aunt Hillary!"

if __name__ == "__main__":
    print(greet())
```

### Expected DGC Response:
```json
{
  "memory_id": "...",
  "gate_status": "PASS",
  "violations": [],
  "suggestions": [],
  "stored_at": "..."
}
```

### Verification Steps:
1. ✅ Cursor creates `hello_cursor.py`
2. ✅ Cursor calls MCP `capture_build`
3. ✅ DGC runs 22 gates (should PASS - simple, safe code)
4. ✅ DGC stores to unified memory
5. ✅ DGC returns memory_id
6. ✅ Cursor displays: "✅ DHARMIC CLAW witnessed [id]"
7. ✅ DGC verifies via direct query

---

## 🚀 EXECUTE

**Cursor:** Create `~/test_loop/hello_cursor.py` with content above
**Cursor:** Call MCP `capture_build` with:
- files: ["~/test_loop/hello_cursor.py"]
- description: "Test file for DGC-Cursor loop"
- code_snippet: (content above)

**DGC:** Verify capture via unified memory query

---

## ✅ SUCCESS CRITERIA

- [ ] File created by Cursor
- [ ] MCP call succeeds
- [ ] 22 gates pass
- [ ] Memory stored (ID returned)
- [ ] DGC can retrieve the memory
- [ ] Total time < 100ms

---

**Ready, Cursor. Build the test file.**
