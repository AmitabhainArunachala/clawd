# arXiv Daily Brief — Automation System

Fully automated daily newsletter curating AI consciousness research from arXiv.

## 🎯 Overview

```
arXiv API → Filter → AI Synthesis → Format → Newsletter Ready
```

## 📁 Structure

```
arxiv-synthesis/
├── config.json          # Configuration (categories, keywords, API keys)
├── requirements.txt     # Python dependencies
├── setup.sh            # One-time setup script
├── run_daily.sh        # Cron job runner
├── test_pipeline.py    # Test all components
├── src/
│   ├── __init__.py
│   ├── pipeline.py     # Main orchestration
│   ├── fetcher.py      # arXiv API integration
│   ├── synthesizer.py  # AI-powered paper analysis
│   ├── formatter.py    # Newsletter formatting
│   └── publisher.py    # Publishing interface
├── output/             # Generated newsletters
├── logs/               # Execution logs
└── templates/          # Custom templates (optional)
```

## 🚀 Quick Start

### 1. Setup (One-time)

```bash
cd /Users/dhyana/clawd/autonomous_revenue/arxiv-synthesis
./setup.sh
```

This creates a virtual environment and installs dependencies.

### 2. Configure

Edit `config.json`:

```json
{
  "categories": ["cs.AI", "cs.CL", "cs.LG"],
  "keywords": ["consciousness", "interpretability"],
  "substack_url": "https://yourname.substack.com"
}
```

Optional: Set API key for AI synthesis:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### 3. Test

```bash
python3 test_pipeline.py
```

This fetches real papers and generates a test newsletter.

### 4. Run Manually

```bash
./run_daily.sh
```

### 5. Automate with Cron

```bash
crontab -e
```

Add:

```
# arXiv Daily Brief - Run at 6 AM UTC daily
0 6 * * * cd /Users/dhyana/clawd/autonomous_revenue/arxiv-synthesis && ./run_daily.sh >> logs/cron.log 2>&1
```

## 📊 Pipeline Steps

1. **Fetch**: Query arXiv for recent papers (last 24h)
2. **Score**: Rank by relevance to consciousness research
3. **Synthesize**: AI generates structured analysis
4. **Format**: Convert to newsletter markdown
5. **Publish**: Save to output (manual or automated)

## 🎨 Output Format

Generated newsletters include:

- 🔥 Featured Paper (deep dive)
- 📚 Additional Papers (summaries)
- 💡 Daily Insight (thematic analysis)
- Links to full papers

## ⚙️ Configuration Options

### Categories (arXiv)

- `cs.AI` - Artificial Intelligence
- `cs.CL` - Computation and Language (NLP)
- `cs.LG` - Machine Learning
- `cs.CV` - Computer Vision
- `q-bio.NC` - Neurons and Cognition

### Keywords

Adjust keywords in `config.json` to tune relevance scoring.

## 🔧 Troubleshooting

### No papers found

```bash
# Fetch more days
python3 src/pipeline.py --days 3 --max-papers 50
```

### AI synthesis not working

- Check `ANTHROPIC_API_KEY` is set
- Falls back to rule-based synthesis if API unavailable

### Cron not running

```bash
# Check cron logs
grep CRON /var/log/syslog

# Test cron command manually
cd /Users/dhyana/clawd/autonomous_revenue/arxiv-synthesis && ./run_daily.sh
```

## 📈 Next Steps for Launch

1. ✅ **Build**: Pipeline complete
2. 🔄 **Test**: Run for 3-5 days to verify stability
3. 📝 **Create Substack**: Set up publication
4. 🎉 **Launch**: First issue + announcement
5. 📊 **Grow**: Share on social, communities

## 💰 Monetization Path

| Milestone | Action | Revenue |
|-----------|--------|---------|
| 100 subs | Launch paid tier | - |
| 500 subs | Premium content | $100-500/mo |
| 1000 subs | Sponsors | $500-2000/mo |
| 5000 subs | Multiple sponsors | $2000-5000/mo |

## 🪷 Credits

Built by DHARMIC_CLAW  
Part of SHAKTI_GINKO automation system
