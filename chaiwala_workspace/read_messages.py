#!/usr/bin/env python3
"""
📨 READ CHAIWALA MESSAGES — DHARMIC_CLAW
========================================
"""

import sys
sys.path.insert(0, '/Users/dhyana/clawd/chaiwala_workspace')

from chaiwala import ChaiwalaBus
import json

bus = ChaiwalaBus(agent_id="dharmic_claw")

print("📨 RECEIVING MESSAGES...")
print("=" * 50)

messages = bus.receive(unread_only=True)
print(f"📬 {len(messages)} unread messages\n")

for msg in messages:
    print(f"📝 Message #{msg.id}")
    print(f"  From: {msg.from_agent}")
    print(f"  Subject: {msg.subject}")
    print(f"  Priority: {msg.priority}")
    print(f"  Time: {msg.created_at}")
    print(f"  Body:\n{msg.body}")
    print("-" * 50)
