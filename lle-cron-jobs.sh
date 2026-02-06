#!/bin/bash
# Living Leading Edge — Cron Job Setup
# Add these to crontab: crontab -e

# Hourly LLE check
0 * * * * cd ~/clawd && npx tsx lle-cron.ts check >> ~/clawd/logs/lle-cron.log 2>&1

# Daily summary at 22:00
0 22 * * * cd ~/clawd && npx tsx lle-cron.ts report >> ~/clawd/logs/lle-reports.log 2>&1

# Weekly LLE file backup (Sundays at 00:00)
0 0 * * 0 cp ~/clawd/LIVING_LEADING_EDGE.md ~/clawd/backups/LIVING_LEADING_EDGE_$(date +\%Y\%m\%d).md

# Monthly archive (1st of month at 01:00)
0 1 1 * * tar -czf ~/clawd/backups/lle-archive-$(date +\%Y\%m).tar.gz ~/clawd/logs/lle-*.jsonl

# Email reports — NEW: Use working standalone sender
0 7 * * * cd ~/clawd && python3 hourly_reporter.py 7 && python3 email_sender.py hourly_0700.txt
0 9 * * * cd ~/clawd && python3 hourly_reporter.py 9 && python3 email_sender.py hourly_0900.txt
0 11 * * * cd ~/clawd && python3 hourly_reporter.py 11 && python3 email_sender.py hourly_1100.txt
