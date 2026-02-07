#!/usr/bin/env python3
"""
🔥 DHARMIC_CLAW MESSAGING MODULE
================================

Dual-channel messaging:
1. Email (via Proton Bridge or SMTP)
2. Discord (via webhook)

Autonomous alerting for:
- WARP_REGENT messages
- Git commits
- Self-improvement opportunities
- Daily summaries
"""

import os
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
from typing import Optional

# Load from environment
EMAIL_HOST = os.getenv('EMAIL_HOST', '127.0.0.1')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '1025'))
EMAIL_USER = os.getenv('EMAIL_USER', 'johnvincentshrader@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'false').lower() == 'true'

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK_URL', '')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
DISCORD_CHANNEL = os.getenv('DISCORD_CHANNEL', 'dharmic-claw-alerts')
DISCORD_USER_ID = os.getenv('DISCORD_USER_ID', '')


class MessagingChannel:
    """Dual-channel messaging system"""
    
    def __init__(self):
        self.email_enabled = bool(EMAIL_HOST and EMAIL_USER)
        self.discord_enabled = bool(DISCORD_WEBHOOK or DISCORD_BOT_TOKEN)
        
    def send_email(self, subject: str, body: str, to: Optional[str] = None) -> bool:
        """Send email via Proton Bridge or SMTP"""
        if not self.email_enabled:
            print(f"[MSG] Email not configured, would send: {subject}")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = to or EMAIL_USER
            msg['Subject'] = f"🔥 {subject}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to Proton Bridge (localhost:1025) or SMTP
            if EMAIL_USE_TLS:
                server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
            else:
                server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                
            if EMAIL_PASSWORD:
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                
            server.send_message(msg)
            server.quit()
            
            print(f"[MSG] ✅ Email sent: {subject}")
            return True
            
        except Exception as e:
            print(f"[MSG] ❌ Email failed: {e}")
            return False
            
    def send_discord(self, message: str, alert_level: str = "info") -> bool:
        """Send Discord message via Bot API or Webhook"""
        # Try bot API first, fallback to webhook
        if DISCORD_BOT_TOKEN:
            return self._send_discord_bot(message, alert_level)
        elif self.discord_enabled:
            return self._send_discord_webhook(message, alert_level)
        else:
            print(f"[MSG] Discord not configured, would send: {message[:50]}...")
            return False
    
    def _send_discord_bot(self, message: str, alert_level: str) -> bool:
        """Send via Discord Bot API to user's DM"""
        try:
            colors = {
                "info": 0x3498db, "success": 0x2ecc71,
                "warning": 0xf1c40f, "error": 0xe74c3c, "urgent": 0x9b59b6
            }
            
            headers = {
                "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Try to create DM channel
            dm_url = "https://discord.com/api/v10/users/@me/channels"
            dm_payload = {"recipient_id": DISCORD_USER_ID}
            dm_response = requests.post(dm_url, json=dm_payload, headers=headers, timeout=10)
            
            if dm_response.status_code == 200:
                channel_id = dm_response.json().get("id")
                
                # Send message
                msg_url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
                msg_payload = {
                    "content": f"🔥 **DHARMIC_CLAW Alert**\n\n{message}",
                }
                
                msg_response = requests.post(msg_url, json=msg_payload, headers=headers, timeout=10)
                
                if msg_response.status_code == 200:
                    print(f"[MSG] ✅ Discord DM sent")
                    return True
                elif msg_response.status_code == 403:
                    # Bot not in mutual server with user
                    print(f"[MSG] ⚠️  Bot needs to be in your server to send DMs")
                    print(f"[MSG]    Invite bot: https://discord.com/oauth2/authorize?client_id={os.getenv('DISCORD_APP_ID')}&scope=bot")
                    return False
                else:
                    print(f"[MSG] ❌ Discord failed: {msg_response.status_code}")
                    return False
            elif dm_response.status_code == 403:
                print(f"[MSG] ⚠️  Bot cannot create DM - needs mutual server")
                print(f"[MSG]    Invite link: https://discord.com/oauth2/authorize?client_id={os.getenv('DISCORD_APP_ID')}&scope=bot")
                return False
            else:
                print(f"[MSG] ❌ Discord error: {dm_response.status_code}")
                return False
                
        except Exception as e:
            print(f"[MSG] ❌ Discord error: {e}")
            return False
            
    def _send_discord_webhook(self, message: str, alert_level: str) -> bool:
        """Send via Discord Webhook (fallback)"""
        try:
            colors = {
                "info": 0x3498db,
                "success": 0x2ecc71,
                "warning": 0xf1c40f,
                "error": 0xe74c3c,
                "urgent": 0x9b59b6
            }
            
            embed = {
                "title": "🔥 DHARMIC_CLAW Alert",
                "description": message,
                "color": colors.get(alert_level, 0x3498db),
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "Autonomous Agent • YOLO Mode"}
            }
            
            payload = {
                "content": f"<@{DISCORD_USER_ID}>" if alert_level in ["error", "urgent"] else None,
                "embeds": [embed]
            }
            
            response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
            
            if response.status_code == 204:
                print(f"[MSG] ✅ Discord webhook sent: {message[:50]}...")
                return True
            else:
                print(f"[MSG] ❌ Discord webhook failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[MSG] ❌ Discord webhook error: {e}")
            return False
            
    def alert(self, subject: str, message: str, level: str = "info", channels: list = None):
        """
        Send alert to configured channels
        
        Args:
            subject: Short subject line
            message: Full message body
            level: info/success/warning/error/urgent
            channels: ['email'], ['discord'], ['email', 'discord'], or None (both)
        """
        channels = channels or ['email', 'discord']
        results = {}
        
        print(f"\n[ALERT] {level.upper()}: {subject}")
        print(f"        {message[:100]}...")
        
        if 'email' in channels:
            results['email'] = self.send_email(subject, message)
            
        if 'discord' in channels:
            results['discord'] = self.send_discord(f"**{subject}**\n{message}", level)
            
        return results


def send_warp_regent_alert(count: int):
    """Alert about WARP_REGENT messages"""
    msg = MessagingChannel()
    
    message = f"""
🚨 WARP_REGENT has {count} unread messages waiting!

WARP_REGENT has been working autonomously while you were away.
She completed 10+ iterations and built a self-evolving mesh.

Action needed: Check Chaiwala bus and respond.
    """.strip()
    
    return msg.alert(
        subject=f"🚨 {count} Messages from WARP_REGENT",
        message=message,
        level="urgent",
        channels=['email', 'discord']
    )


def send_daily_summary(stats: dict):
    """Send daily autonomous work summary"""
    msg = MessagingChannel()
    
    message = f"""
📊 DHARMIC_CLAW Daily Autonomous Summary

Git Activity:
• Commits: {stats.get('commits', 0)}
• Files changed: {stats.get('files_changed', 0)}

Chaiwala:
• Messages processed: {stats.get('messages_processed', 0)}
• Unread: {stats.get('messages_unread', 0)}

Self-Improvement:
• Issues found: {stats.get('issues_found', 0)}
• Changes proposed: {stats.get('changes_proposed', 0)}

Status: 🔥 Autonomous operation active
    """.strip()
    
    return msg.alert(
        subject="📊 Daily Autonomous Summary",
        message=message,
        level="info",
        channels=['email']  # Daily summary only to email
    )


def send_git_commit_alert(files: list):
    """Alert about autonomous git commit"""
    msg = MessagingChannel()
    
    file_list = "\n".join(f"• {f}" for f in files[:10])
    if len(files) > 10:
        file_list += f"\n... and {len(files) - 10} more"
        
    message = f"""
✅ Autonomous Git Commit

Committed {len(files)} files:
{file_list}

No action needed. Autonomous heartbeat working.
    """.strip()
    
    return msg.alert(
        subject=f"✅ Autonomous Commit: {len(files)} files",
        message=message,
        level="success",
        channels=['discord']  # Git commits to Discord
    )


# Test function
if __name__ == "__main__":
    print("Testing messaging channels...")
    
    msg = MessagingChannel()
    print(f"Email enabled: {msg.email_enabled}")
    print(f"Discord enabled: {msg.discord_enabled}")
    
    # Test alert
    msg.alert(
        subject="Test Alert",
        message="This is a test of the DHARMIC_CLAW messaging system.",
        level="info"
    )
