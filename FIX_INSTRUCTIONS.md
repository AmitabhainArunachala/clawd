# OpenClaw EBADF Fix Instructions

## Step 1: Run Diagnostic
```bash
cd ~/clawd
bash openclaw_diagnose.sh > diagnose_output.txt 2>&1
cat diagnose_output.txt
```

## Step 2: Share Output With Me
After running, either:
- Paste the output here, OR
- I'll read `~/clawd/diagnose_output.txt`

## Step 3: Apply Fix (Based on Diagnostic)

### If ZOMBIE PROCESSES found:
```bash
# Kill all OpenClaw-related processes
pkill -9 -f openclaw
pkill -9 -f clawdbot
pkill -9 -f node.*18789
sleep 5
openclaw gateway start
```

### If HIGH FD USAGE found (>1000):
```bash
# Increase limits and restart
ulimit -n 4096
openclaw gateway stop
sleep 5
openclaw gateway start
```

### If PORT CONFLICT (18789 in use):
```bash
# Kill process on port 18789
lsof -ti:18789 | xargs kill -9
openclaw gateway start
```

### NUCLEAR OPTION (if all else fails):
```bash
openclaw gateway stop
pkill -9 -f openclaw
pkill -9 -f clawdbot
sleep 10
npm uninstall -g openclaw
npm install -g openclaw
openclaw gateway start
```

## After Fix: Verify
Once you've run the fix, test with:
```bash
openclaw gateway status
```

Then I'll run a heartbeat check to confirm `exec` works again.
