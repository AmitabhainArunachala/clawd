# INTEGRATION_SKILL_BRIDGE.md
**Bridge:** Clawdbot ↔ 44 Skills  
**Status:** ✅ OPERATIONAL  
**Path:** `~/clawd/skill-bridge.py`  
**Last Verified:** 2026-02-17

---

## Purpose
Unified skill launcher that makes all 44+ skills executable by detecting type and launching correctly. Eliminates "I don't know how to run this skill" friction.

## Cross-System Compatibility

### Input (Skill Types)
| Type | Detection | Count | Example |
|------|-----------|-------|---------|
| CLI | `cli.py` exists | ~5 | `dgc`, `obsidian` |
| Package | `__init__.py` exists | ~8 | `mech-interp` |
| Installable | `setup.py` / `pyproject.toml` | ~3 | `universal-inference-runtime` |
| Documentation | `SKILL.md` only | ~28 | Most skills |
| Unknown | None of above | ~0 | — |

### Output (Launch Methods)
| Type | Launch Method | Status |
|------|---------------|--------|
| CLI | `python cli.py [args]` | ✅ Working |
| Package | `import module; module.main(args)` | ✅ Working |
| Installable | `python -m module [args]` | ✅ Working |
| Documentation | Print path to SKILL.md | ✅ Working |

## API Surface

```bash
# List all skills
python skill-bridge.py -l

# Launch skill with args
python skill-bridge.py <skill-name> [args...]
```

```python
from skill_bridge import launch_skill, detect_skill_type, list_skills

return_code = launch_skill("mech-interp", ["--help"])
```

## Integration Points

1. **OpenClaw Integration**: Available as `openclaw skill <name>` alias
2. **Cron Jobs**: Used by `meta-cognition-deep-read` to invoke research skills
3. **Subagents**: Spawned sessions use skill-bridge for tool access
4. **Discovery**: Auto-detects new skills added to `~/clawd/skills/`

## Dead Skill Detection (Kaizen Hook)
Skills with only `SKILL.md` (no code) = documentation-only:
- Count: ~28 of 44 (64% documentation-only)
- Action: Flag for archival if unused 90+ days
- List: Run `python skill-bridge.py -l | grep "📖"`

## Test Coverage
- Manual: ✅ All skill types tested
- Automated: ⚠️ No automated test suite
- Integration: ✅ Used daily by cron jobs

## Known Limitations
1. No dependency resolution — skills must install their own deps
2. No version pinning — uses whatever is installed
3. No sandboxing — skills run with full user permissions
4. Documentation-only skills give false sense of capability

## Health Check
```bash
cd ~/clawd
python skill-bridge.py -l | tail -5
```

---
**Next Review:** 2026-02-24  
**Owner:** INTEGRATOR subagent  
**Action:** Archive 20+ dead skills flagged by Kaizen
