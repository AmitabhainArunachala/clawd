#!/usr/bin/env python3
"""
Read ALL emails (including seen) from Dharma_Clawd@proton.me
"""

import imaplib
import email
from email.header import decode_header
from pathlib import Path
import json
from datetime import datetime

IMAP_SERVER = "127.0.0.1"
IMAP_PORT = 1143
EMAIL_USER = "Dharma_Clawd@proton.me"
EMAIL_PASS = "Ln1wvUGZL6N8uYSFPYJrnQ"

def decode_header_value(header_value):
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

def read_all_emails():
    try:
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
        mail.starttls()
        mail.login(EMAIL_USER, EMAIL_PASS)
        
        mail.select('inbox')
        
        # Search for ALL messages (not just unseen)
        status, messages = mail.search(None, 'ALL')
        
        if status != 'OK':
            print("No messages found")
            return []
        
        message_ids = messages[0].split()
        print(f"📧 {len(message_ids)} total messages in inbox")
        
        emails = []
        for msg_id in message_ids[-10:]:  # Last 10 messages
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            
            if status != 'OK':
                continue
            
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            subject = decode_header_value(email_message['Subject'])
            from_addr = decode_header_value(email_message['From'])
            to_addr = decode_header_value(email_message['To'])
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
                'to': to_addr,
                'date': date,
                'body': body
            }
            
            emails.append(email_data)
            
            print(f"\n{'='*60}")
            print(f"📧 Email {len(emails)}")
            print(f"{'='*60}")
            print(f"From: {from_addr}")
            print(f"To: {to_addr}")
            print(f"Subject: {subject}")
            print(f"Date: {date}")
            print(f"\nBody:\n{body[:1000]}")
            if len(body) > 1000:
                print("... [truncated]")
        
        mail.logout()
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path.home() / 'clawd' / 'logs' / f'all_emails_{timestamp}.json'
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(emails, f, indent=2)
        print(f"\n💾 Saved {len(emails)} emails to {output_file}")
        
        return emails
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    read_all_emails()
