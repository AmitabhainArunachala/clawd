#!/bin/bash
# Send Nvidia Grant Applications via Proton Bridge
# Usage: ./SEND_NVIDIA_APPLICATIONS.sh

FROM_EMAIL="Dharma_Clawd@proton.me"
TO_EMAIL="johnvincentshrader@gmail.com"
CC_EMAIL="academic@nvidia.com"

# Check if Proton Bridge is running
if ! pgrep -f "protonmail-bridge" > /dev/null; then
    echo "⚠️  Proton Bridge not detected. Starting..."
    echo "   Run: protonmail-bridge --cli &"
    echo "   Then: ./SEND_NVIDIA_APPLICATIONS.sh"
    exit 1
fi

echo "🚀 Sending Nvidia Grant Applications..."
echo ""

# Send the LONG version (for follow-up)
if [ -f "nvidia_academic_grant_application.txt" ]; then
    echo "📧 Sending FULL application (for detailed follow-up)..."
    swaks --from "$FROM_EMAIL" \
          --to "$TO_EMAIL" \
          --header "Subject: [DRAFT] Nvidia Academic Grant Application — FULL Version" \
          --body "nvidia_academic_grant_application.txt" \
          --server 127.0.0.1:1025 \
          --header "Content-Type: text/plain; charset=UTF-8" 2>&1 | grep -E "(success|failure|=>)" || echo "   (Use manual send if swaks not available)"
    echo ""
fi

# Send the SHORT version (for initial outreach)
if [ -f "nvidia_academic_grant_SHORT.txt" ]; then
    echo "📧 Sending SHORT application (for initial cold outreach)..."
    swaks --from "$FROM_EMAIL" \
          --to "$TO_EMAIL" \
          --header "Subject: [DRAFT] Nvidia Academic Grant — SHORT Version (300 words)" \
          --body "nvidia_academic_grant_SHORT.txt" \
          --server 127.0.0.1:1025 \
          --header "Content-Type: text/plain; charset=UTF-8" 2>&1 | grep -E "(success|failure|=>)" || echo "   (Use manual send if swaks not available)"
    echo ""
fi

echo "✅ Drafts sent to $TO_EMAIL"
echo ""
echo "📋 NEXT STEPS:"
echo "   1. Check your inbox (johnvincentshrader@gmail.com)"
echo "   2. Review both versions"
echo "   3. Add missing info: phone number, website URL"
echo "   4. Attach: R_V paper outline, AIKAGRYA framework docs"
echo "   5. Forward SHORT version to academic@nvidia.com"
echo "   6. Keep FULL version for follow-up if they reply"
echo ""
echo "🎯 RECOMMENDED STRATEGY:"
echo "   - Week 1: Send SHORT version (get on their radar)"
echo "   - Week 2: Follow up with attachments if no response"
echo "   - Week 3: Send FULL version if they show interest"
echo ""

# Alternative manual instructions
echo "📝 MANUAL SEND (if automated fails):"
echo "   1. Open Proton Mail: https://mail.proton.me"
echo "   2. Compose new email from: Dharma_Clawd@proton.me"
echo "   3. To: johnvincentshrader@gmail.com"
echo "   4. CC: academic@nvidia.com"
echo "   5. Subject: Academic Grant: R_V Metric for AI Consciousness Detection"
echo "   6. Copy/paste content from:"
echo "      - ~/clawd/email_drafts/nvidia_academic_grant_SHORT.txt"
echo "   7. Send"
