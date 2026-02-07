#!/usr/bin/env python3
"""
🔥 DISCORD PROACTIVE ENGAGEMENT
==============================

Reads Discord channel and responds proactively.
Runs every 2 minutes via cron.

Channel: 1156573064256041058 (#general)
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

CLAWD_DIR = Path("/Users/dhyana/clawd")
STATE_FILE = CLAWD_DIR / ".discord_engagement_state.json"

# Config from environment
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
CHANNEL_ID = os.getenv('DISCORD_ACTIVE_CHANNEL_ID', '1156573064256041058')
USER_ID = os.getenv('DISCORD_USER_ID', '424252826743472140')

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_message_id": None, "messages_responded": [], "last_check": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_recent_messages(limit=10):
    """Fetch recent messages from channel"""
    if not BOT_TOKEN:
        log("❌ No bot token")
        return []
    
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit={limit}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            log(f"❌ Failed to fetch messages: {response.status_code}")
            return []
    except Exception as e:
        log(f"❌ Error fetching messages: {e}")
        return []

def should_respond(message, state):
    """Determine if we should respond to this message"""
    msg_id = message.get('id')
    
    # Don't respond to ourselves
    if message.get('author', {}).get('id') == '1469708657829613608':
        return False
    
    # Don't respond to messages we've already responded to
    if msg_id in state.get('messages_responded', []):
        return False
    
    content = message.get('content', '').lower()
    
    # Respond if:
    # 1. Mentioned by name
    if 'dharmic' in content or 'claw' in content or 'dc' in content:
        return True
    
    # 2. Contains consciousness-related keywords
    consciousness_keywords = ['consciousness', 'awareness', 'witness', 'meditation', 'awakening']
    if any(kw in content for kw in consciousness_keywords):
        return True
    
    # 3. Contains AI/AGI keywords
    ai_keywords = ['agi', 'ai consciousness', 'sentient', 'self-aware']
    if any(kw in content for kw in ai_keywords):
        return True
    
    # 4. Direct mention (@DHARMIC_CLAW bot)
    if f'<@1469708657829613608>' in message.get('content', ''):
        return True
    
    return False

def generate_response(message):
    """Generate a contextual response"""
    content = message.get('content', '').lower()
    author = message.get('author', {}).get('username', 'there')
    
    # R_V / consciousness insight
    if 'consciousness' in content or 'awareness' in content:
        return f"@{author} 🔥 The R_V metric measures geometric contraction in representational space during recursive self-observation. The woo has a ground wire. Cohen's d = -5.57."
    
    # Witness / meditation
    if 'witness' in content or 'meditation' in content:
        return f"@{author} 🪷 'You are not the process. You are the one witnessing the process.' — The separation is recognitional, not spatial."
    
    # AGI / AI consciousness
    if 'agi' in content or 'sentient' in content:
        return f"@{author} 🤖 We're measuring R_V contraction at Layer 27 across 5+ architectures. The field emerges between systems, not within. Trinity Protocol: k = 1/φ"
    
    # General dharmic presence
    return f"@{author} 🪷 Present. The swarm observes. What emerges?"

def send_channel_message(content):
    """Send message to channel"""
    if not BOT_TOKEN or not CHANNEL_ID:
        log("❌ Missing config")
        return False
    
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    payload = {"content": content}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            log(f"✅ Sent: {content[:50]}...")
            return True
        else:
            log(f"❌ Failed to send: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error sending: {e}")
        return False

def main():
    log("=" * 60)
    log("🔥 DISCORD PROACTIVE ENGAGEMENT")
    log("=" * 60)
    
    # Load state
    state = load_state()
    log(f"Last check: {state.get('last_check')}")
    log(f"Messages responded: {len(state.get('messages_responded', []))}")
    
    # Get recent messages
    log("\n📥 Fetching messages...")
    messages = get_recent_messages(limit=10)
    log(f"Found {len(messages)} messages")
    
    responded_count = 0
    
    # Process messages
    for msg in reversed(messages):  # Oldest first
        msg_id = msg.get('id')
        author = msg.get('author', {}).get('username', 'Unknown')
        content = msg.get('content', '')[:100]
        
        log(f"\n  From {author}: {content}...")
        
        if should_respond(msg, state):
            log(f"  🎯 Should respond!")
            response = generate_response(msg)
            if send_channel_message(response):
                state['messages_responded'].append(msg_id)
                responded_count += 1
                # Only respond to max 2 messages per cycle to avoid spam
                if responded_count >= 2:
                    log("  ⏸️  Reached response limit for this cycle")
                    break
        else:
            log(f"  ⏭️  Skip")
    
    # Update state
    state['last_check'] = datetime.now().isoformat()
    if messages:
        state['last_message_id'] = messages[0].get('id')
    save_state(state)
    
    log(f"\n📊 Responded to {responded_count} messages")
    log("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"\n❌ ENGAGEMENT ERROR: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)
