# CRITICAL FIXES NEEDED NOW

Based on failure analysis, these issues are **immediately dangerous**:

## 1. API Key Exposure (CRITICAL)

**Problem**: Your Anthropic API key is visible in plaintext:
```
/Users/dhyana/Library/LaunchAgents/com.clawdbot.gateway.plist
Line 30: sk-ant-api03-f4cIvXaEEYtLD7-1MlXD4xTof9PRm868h2KYBjm5gSic-xKq1v8Y6YjawhvdeRjgwlg8lRHCU4VvRMTu8eAazg-hOyPcAAA
```

**Risk**: Anyone with access to your Mac can steal this key and run up your bill.

**Fix**:
```bash
# Option 1: Use environment file
echo 'ANTHROPIC_API_KEY=sk-ant-...' > ~/.clawdbot/.env
chmod 600 ~/.clawdbot/.env

# Option 2: Use macOS keychain
security add-generic-password -a "$USER" -s "clawdbot" -w "sk-ant-..."

# Then edit plist to remove the key and source from file
```

## 2. unified_daemon Crashed (HIGH)

**Problem**: The dharmic agent core is not running:
```
RuntimeError: Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code
```

**Fix**:
```bash
# Option 1: Install Claude CLI (if you want to use it)
npm install -g @anthropic-ai/claude-code

# Option 2: Use Max CLI instead
# (But Max isn't installed either - `which max` returns nothing)

# Option 3: Use API directly (edit model_backend.py to skip CLI check)

# Restart after fixing
launchctl kickstart -k gui/$(id -u)/com.dharmic.unified-daemon
```

## 3. No Dead Man's Switch (CRITICAL)

**Problem**: System could be down for days and you wouldn't know.

**Fix**:
```bash
# Install the check_heartbeat.sh script to cron
crontab -e
# Add: 0 * * * * /Users/dhyana/clawd/scripts/check_heartbeat.sh

# Or use healthchecks.io
# 1. Sign up at https://healthchecks.io (free)
# 2. Get your ping URL
# 3. Add to heartbeat loop:
#    curl -fsS --retry 3 https://hc-ping.com/YOUR-UUID-HERE

# Then if no ping for X hours, healthchecks.io alerts you via email
```

## 4. Mac Sleep Enabled (HIGH)

**Problem**: Mac sleeps after 10min, all daemons stop, no alerts.

**Fix**:
```bash
# Option 1: Disable sleep entirely
sudo pmset -a sleep 0
sudo pmset -a disksleep 0
sudo pmset -a displaysleep 0

# Option 2: Use caffeinate in LaunchAgent
# Edit plist ProgramArguments to:
# <string>caffeinate</string>
# <string>-i</string>
# <string>/path/to/your/daemon</string>

# Option 3: Keep display on, allow system sleep but prevent app nap
defaults write NSGlobalDomain NSAppSleepDisabled -bool YES
```

## 5. Claude CLI Timeouts (MEDIUM - Happening Frequently)

**Problem**: 4 timeouts today, falling back to generic responses.

**Observed**:
```
[2026-02-03 12:39:12] Claude CLI timeout after 180s, using fallback
[2026-02-03 13:00:17] Claude CLI timeout after 180s, using fallback
[2026-02-03 13:26:19] Claude CLI timeout after 180s, using fallback
[2026-02-03 18:20:17] Claude CLI timeout after 180s, using fallback
```

**Fix**:
```python
# Edit /Users/dhyana/DHARMIC_GODEL_CLAW/src/core/model_backend.py
# Increase timeout from 180 to 300 or 600
# Or switch to API calls instead of CLI
```

---

## Priority Order

1. Fix API key exposure (10 min)
2. Disable Mac sleep (2 min)
3. Set up dead man's switch (15 min)
4. Fix unified_daemon crash (30 min - depends on which backend you want)
5. Fix Claude CLI timeouts (10 min)

**Total time to fix critical issues: ~1 hour**

Then test:
```bash
# Send email to vijnan.shakti@pm.me
# Should get response within 5 minutes
# Check logs show no timeouts
# Check healthchecks.io shows green ping
# Let Mac sit idle for 15 minutes
# Verify daemons still running
```

