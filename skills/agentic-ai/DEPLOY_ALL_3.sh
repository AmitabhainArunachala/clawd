#!/bin/bash
# DEPLOY_AGENTIC_AI_GOLD.sh — Execute all 3 deployments

echo "🚀 AGENTIC AI GOLD STANDARD — Deployment Script"
echo "================================================"
echo ""

# ==================== TASK 1: CLAWHUB PUBLISH ====================
echo "📦 TASK 1: ClawHub Publishing"
echo "------------------------------"
echo ""
echo "Step 1: Go to https://clawhub.com"
echo "Step 2: Create account (email + password)"
echo "Step 3: Click 'Publish New Skill'"
echo "Step 4: Upload files from: ~/clawd/skills/agentic-ai/CLAWHUB_PACKAGE/"
echo ""
echo "Skill Details:"
echo "  Name: AGENTIC AI GOLD STANDARD"
echo "  Slug: agentic-ai-gold"
echo "  Category: AI & LLMs > Agent Frameworks"
echo "  Tags: agent, ai, langgraph, mcp, a2a, autonomous, self-improving"
echo ""
echo "Pricing:"
echo "  Starter: $49 (one-time)"
echo "  Professional: $149 (one-time) ⭐"
echo "  Enterprise: $499 (one-time)"
echo ""
echo "Launch Offer:"
echo "  Code: SHAKTI50 (50% off first 100 customers)"
echo ""

# ==================== TASK 2: LAUNCH POSTS ====================
echo ""
echo "📢 TASK 2: Launch Posts (Copy-Paste Ready)"
echo "-------------------------------------------"
echo ""

echo "=== TWITTER ==="
echo "(Copy this exactly):"
cat ~/clawd/skills/agentic-ai/LAUNCH_MATERIALS/tweet_launch.txt
echo ""

echo "=== HACKER NEWS (Show HN) ==="
echo "(Copy this exactly):"
cat ~/clawd/skills/agentic-ai/LAUNCH_MATERIALS/hacker_news_showhn.txt
echo ""

echo "=== REDDIT r/OpenClaw ==="
echo "(Copy this exactly):"
cat ~/clawd/skills/agentic-ai/LAUNCH_MATERIALS/reddit_openclaw.txt
echo ""

echo "=== REDDIT r/AI_Agents ==="
echo "(Copy this exactly):"
cat ~/clawd/skills/agentic-ai/LAUNCH_MATERIALS/reddit_aiagents.txt
echo ""

# ==================== TASK 3: LANDING PAGE ====================
echo ""
echo "🌐 TASK 3: Landing Page Deployment"
echo "-----------------------------------"
echo ""

echo "Option A: Netlify Drop (Easiest - 30 seconds)"
echo "  1. Open browser → https://app.netlify.com/drop"
echo "  2. Drag this file onto the page:"
echo "     ~/clawd/skills/agentic-ai/LANDING_PAGE/landing-page.zip"
echo "  3. Get instant URL"
echo ""

echo "Option B: GitHub Pages (Free - 2 minutes)"
echo "  1. Go to https://github.com/new"
echo "  2. Repository name: agentic-ai-gold"
echo "  3. Make it Public"
echo "  4. Upload this file:"
echo "     ~/clawd/skills/agentic-ai/LANDING_PAGE/index.html"
echo "  5. Settings → Pages → Source: Deploy from branch → main"
echo "  6. URL: https://yourusername.github.io/agentic-ai-gold"
echo ""

echo "Option C: Local Preview (Right now)"
echo "  Run this command:"
echo "    cd ~/clawd/skills/agentic-ai/LANDING_PAGE && python3 -m http.server 8080"
echo "  Then open: http://localhost:8080"
echo ""

# ==================== SUMMARY ====================
echo ""
echo "✅ ALL FILES READY"
echo "=================="
echo ""
echo "Location: ~/clawd/skills/agentic-ai/"
echo ""
echo "CLAWHUB_PACKAGE/     → Upload to clawhub.com"
echo "LAUNCH_MATERIALS/    → Copy-paste to Twitter, HN, Reddit"
echo "LANDING_PAGE/        → Deploy to Netlify or GitHub Pages"
echo ""
echo "Estimated time to complete all 3: 5-10 minutes"
echo ""
echo "🎯 Goal: $200/month"
echo "   Need: 9 Starter sales at 50% off = $220"
echo "   OR:   3 Professional sales at 50% off = $223"
echo ""
echo "Good luck! 🚀"
