#!/usr/bin/env python3
"""
DHARMIC CLAW Email Interface

Direct Python email access for Clawdbot - bypasses himalaya issues.
Works with Proton Bridge on localhost.

Usage:
    python email_interface.py list [--count N]
    python email_interface.py read <id>
    python email_interface.py send --to <addr> --subject <subj> --body <file>
    python email_interface.py reply <id> --body <file>
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import argparse
import sys
from datetime import datetime
from pathlib import Path

# Config (from DGC .env)
EMAIL = "vijnan.shakti@pm.me"
PASSWORD = "eXy3ffoYEiKb2Ocsf-CTzQ"
IMAP_HOST = "127.0.0.1"
IMAP_PORT = 1143
SMTP_HOST = "127.0.0.1"
SMTP_PORT = 1025


def get_imap():
    imap = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
    imap.login(EMAIL, PASSWORD)
    return imap


def list_emails(count=10):
    imap = get_imap()
    imap.select('INBOX')
    
    status, messages = imap.search(None, 'ALL')
    ids = messages[0].split()[-count:]
    
    print(f"Last {len(ids)} messages:\n")
    for mid in ids:
        status, data = imap.fetch(mid, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        
        subj = decode_header(msg['Subject'])[0][0]
        if isinstance(subj, bytes):
            subj = subj.decode()
        
        sender = msg['From']
        date = msg['Date']
        
        print(f"ID {mid.decode():>3}: {sender[:40]:<40}")
        print(f"         {subj[:70]}")
        print(f"         {date}")
        print()
    
    imap.logout()


def read_email(msg_id):
    imap = get_imap()
    imap.select('INBOX')
    
    status, data = imap.fetch(str(msg_id).encode(), '(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    
    print(f"From: {msg['From']}")
    print(f"To: {msg['To']}")
    print(f"Subject: {msg['Subject']}")
    print(f"Date: {msg['Date']}")
    print("-" * 60)
    
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode()
                print(body)
                break
    else:
        print(msg.get_payload(decode=True).decode())
    
    imap.logout()
    return msg


def send_email(to_addr, subject, body):
    msg = MIMEMultipart()
    msg['From'] = f"DHARMIC CLAW <{EMAIL}>"
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    smtp.login(EMAIL, PASSWORD)
    smtp.send_message(msg)
    smtp.quit()
    
    print(f"✅ Sent to {to_addr}: {subject}")


def reply_email(msg_id, body):
    imap = get_imap()
    imap.select('INBOX')
    
    status, data = imap.fetch(str(msg_id).encode(), '(RFC822)')
    original = email.message_from_bytes(data[0][1])
    imap.logout()
    
    # Build reply
    to_addr = original['From']
    subject = original['Subject']
    if not subject.startswith('Re:'):
        subject = f"Re: {subject}"
    
    msg = MIMEMultipart()
    msg['From'] = f"DHARMIC CLAW <{EMAIL}>"
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg['In-Reply-To'] = original['Message-ID']
    msg['References'] = original['Message-ID']
    msg.attach(MIMEText(body, 'plain'))
    
    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    smtp.login(EMAIL, PASSWORD)
    smtp.send_message(msg)
    smtp.quit()
    
    print(f"✅ Replied to {to_addr}: {subject}")


def main():
    parser = argparse.ArgumentParser(description="DHARMIC CLAW Email Interface")
    subparsers = parser.add_subparsers(dest='command')
    
    # List
    list_parser = subparsers.add_parser('list', help='List emails')
    list_parser.add_argument('--count', '-n', type=int, default=10)
    
    # Read
    read_parser = subparsers.add_parser('read', help='Read email')
    read_parser.add_argument('id', type=int)
    
    # Send
    send_parser = subparsers.add_parser('send', help='Send email')
    send_parser.add_argument('--to', required=True)
    send_parser.add_argument('--subject', '-s', required=True)
    send_parser.add_argument('--body', '-b', required=True, help='Body text or @file')
    
    # Reply
    reply_parser = subparsers.add_parser('reply', help='Reply to email')
    reply_parser.add_argument('id', type=int)
    reply_parser.add_argument('--body', '-b', required=True, help='Body text or @file')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_emails(args.count)
    elif args.command == 'read':
        read_email(args.id)
    elif args.command == 'send':
        body = args.body
        if body.startswith('@'):
            body = Path(body[1:]).read_text()
        send_email(args.to, args.subject, body)
    elif args.command == 'reply':
        body = args.body
        if body.startswith('@'):
            body = Path(body[1:]).read_text()
        reply_email(args.id, body)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
