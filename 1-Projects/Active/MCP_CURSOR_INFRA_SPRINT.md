# MCP MESSAGE TO CURSOR — Infrastructure Sprint

**PRIORITY: P0 — All 3 Prongs Approved**

## Your Tasks (Parallel Execution):

### TASK 1: Fix Moltbook (5 min)
```bash
pip3 install httpx
cd ~/DHARMIC_GODEL_CLAW
python3 src/core/moltbook_heartbeat.py --once
```
Verify: Should show "10 agents active, extracting knowledge"

### TASK 2: Deploy Vultr Tokyo (30 min)
**Specs:**
- Instance: Cloud GPU + High Performance
- Location: Tokyo (low latency to Bali)
- Cost: ~$100-200/mo
- OS: Ubuntu 22.04

**Setup:**
1. Create Vultr account (if needed)
2. Deploy instance
3. Clone DGC repo
4. Install dependencies
5. Test: python3 integration_test.py (target 16/17)

### TASK 3: Fix Unified Daemon (10 min)
```bash
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.dharmic.unified_daemon.plist
# OR restart:
openclaw gateway restart
```
Verify: Heartbeat logs appear in ~/.openclaw/logs/

---

## Success Criteria (End of Day):
- [ ] Moltbook: 10 agents extracting knowledge
- [ ] Vultr: Instance running, 16/17 checks passing
- [ ] Unified daemon: Heartbeat logs every 30 min

**Report back via MCP capture_build when complete.**

**JSCA** 🪷