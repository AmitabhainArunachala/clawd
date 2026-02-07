#!/usr/bin/env python3
import os
os.environ['DISCORD_BOT_TOKEN'] = 'MTQ2OTcwODY1NzgyOTYxMzYwOA.GuPtsc.FmSh2o6nxnaGciC1zU4WcDGSz2IWayx-KBQXAI'
os.environ['DISCORD_USER_ID'] = '424252826743472140'

from dharmic_claw_messaging import MessagingChannel

msg = MessagingChannel()
message = """🎼 **ORCHESTRATOR REMINDER**

🔥 **R_V TOOLKIT = FOUNDATION**

Status: 80% complete
Action needed: GitHub push (1 hour)
Revenue: $100-500/mo via GitHub Sponsors

**Why this matters:**
• Everything else depends on it
• AIKAGRYA report references it
• ClawHub skills package it
• Consulting credibility requires it

**You said:** "I will forget" — I will remind you every 6 hours.

Ready to execute SUBAGENT_PLAN.md when you say go.

JSCA 🔥"""

msg.send_discord(message, 'warning')
print('✅ Reminder sent to Discord')
