#!/usr/bin/env python3
"""
IMAP Email Reader — Checks Dharma_Clawd@proton.me inbox
Connects to Proton Bridge via IMAP (127.0.0.1:1143, STARTTLS)
"""

import imaplib
import email
from email.header import decode_header
from pathlib import Path
import json
from datetime import datetime

# Proton Bridge IMAP config
IMAP_SERVER = "127.0.0.1"
IMAP_PORT = 1143
EMAIL_USER = "Dharma_Clawd@proton.me"
EMAIL_PASS = "Ln1wvUGZL6N8uYSFPYJrnQ"

def connect_imap():
    """Connect to Proton Bridge IMAP with STARTTLS."""
    try:
        # Connect
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
        
        # STARTTLS
        mail.starttls()
        
        # Login
        mail.login(EMAIL_USER, EMAIL_PASS)
        
        print(f"✅ Connected to IMAP: {EMAIL_USER}")
        return mail
        
    except Exception as e:
        print(f"❌ IMAP connection failed: {e}")
        return None

def decode_header_value(header_value):
    """Decode email header."""
    if header_value is None:
        return ""
    
    try:
        decoded_parts = decode_header(header_value)
        decoded_str = ""
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(charset or 'utf-8', errors='ignore')
            else:
                decoded_str += part
        return decoded_str
    except:
        return str(header_value)

def check_inbox(mail, mark_seen=False):
    """Check for unread emails."""
    try:
        mail.select('inbox')
        
        # Search for unread messages
        status, messages = mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            print("No messages found")
            return []
        
        message_ids = messages[0].split()
        emails = []
        
        print(f"📧 {len(message_ids)} unread messages")
        
        for msg_id in message_ids:
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            
            if status != 'OK':
                continue
            
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract info
            subject = decode_header_value(email_message['Subject'])
            from_addr = decode_header_value(email_message['From'])
            date = email_message['Date']
            
            # Get body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body_bytes = part.get_payload(decode=True)
                        if body_bytes:
                            body = body_bytes.decode('utf-8', errors='ignore')
                        break
            else:
                body_bytes = email_message.get_payload(decode=True)
                if body_bytes:
                    body = body_bytes.decode('utf-8', errors='ignore')
            
            email_data = {
                'id': msg_id.decode(),
                'subject': subject,
                'from': from_addr,
                'date': date,
                'body': body[:500] + '...' if len(body) > 500 else body
            }
            
            emails.append(email_data)
            
            # Mark as seen if requested
            if mark_seen:
                mail.store(msg_id, '+FLAGS', '\\Seen')
        
        return emails
        
    except Exception as e:
        print(f"❌ Failed to check inbox: {e}")
        return []

def save_emails(emails):
    """Save checked emails to file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = Path.home() / 'clawd' / 'logs' / f'emails_{timestamp}.json'
    
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(emails, f, indent=2)
    
    print(f"💾 Saved {len(emails)} emails to {output_file}")

def main():
    """Main entry point."""
    import sys
    
    # Connect to IMAP
    mail = connect_imap()
    if not mail:
        sys.exit(1)
    
    # Check command
    if len(sys.argv) > 1 and sys.argv[1] == 'read':
        # Just check and save, don't show
        emails = check_inbox(mail, mark_seen=False)
        save_emails(emails)
        print(f"✅ Checked {len(emails)} emails without marking as read")
    else:
        # Default: check and display
        emails = check_inbox(mail, mark_seen=False)
        
        if emails:
            print("\n" + "="*60)
            print("📧 UNREAD EMAILS")
            print("="*60)
            
            for i, email_data in enumerate(emails, 1):
                print(f"\n--- Email {i} ---")
                print(f"From: {email_data['from']}")
                print(f"Subject: {email_data['subject']}")
                print(f"Date: {email_data['date']}")
                print(f"\nBody:\n{email_data['body'][:300]}")
            
            save_emails(emails)
        else:
            print("✅ No unread emails")
    
    # Logout
    mail.logout()
    print("\n👋 IMAP connection closed")

if __name__ == "__main__":
    main()
