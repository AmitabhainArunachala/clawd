# Cron Setup Instructions

## Option 1: System Cron (Recommended)

Edit your crontab:

```bash
crontab -e
```

Add this line for daily 6 AM UTC:

```
0 6 * * * cd /Users/dhyana/clawd/autonomous_revenue/arxiv-synthesis && /bin/bash run_daily.sh >> logs/cron.log 2>&1
```

Or for 9 AM local time:

```
0 9 * * * cd /Users/dhyana/clawd/autonomous_revenue/arxiv-synthesis && /bin/bash run_daily.sh >> logs/cron.log 2>&1
```

## Option 2: User LaunchAgent (macOS)

Create `~/Library/LaunchAgents/com.dharmicclaw.arxiv-brief.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dharmicclaw.arxiv-brief</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/dhyana/clawd/autonomous_revenue/arxiv-synthesis/run_daily.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/dhyana/clawd/autonomous_revenue/arxiv-synthesis</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/dhyana/clawd/autonomous_revenue/arxiv-synthesis/logs/launchd.out</string>
    <key>StandardErrorPath</key>
    <string>/Users/dhyana/clawd/autonomous_revenue/arxiv-synthesis/logs/launchd.err</string>
</dict>
</plist>
```

Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.dharmicclaw.arxiv-brief.plist
launchctl start com.dharmicclaw.arxiv-brief
```

## Option 3: GitHub Actions (Free Cloud)

Create `.github/workflows/daily-brief.yml`:

```yaml
name: arXiv Daily Brief

on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily
  workflow_dispatch:  # Manual trigger

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Generate brief
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python3 src/pipeline.py --skip-publish
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: daily-brief
          path: output/latest.md
```

## Verification

Check if cron is set up:

```bash
crontab -l
```

View recent logs:

```bash
tail -f logs/cron.log
```

Test manually:

```bash
./run_daily.sh
```
