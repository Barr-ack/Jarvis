"""
Communication Handler
Handles email, WhatsApp, and other communication operations
"""

import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import pywhatkit as kit
from dotenv import load_dotenv

load_dotenv()
GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")


class Communication:
    def __init__(self):
        pass
    
    def send_email(self, to_email, subject, body, cc=None):
        """Send email using Gmail SMTP"""
        try:
            if not GMAIL_USERNAME or not GMAIL_PASSWORD:
                return {"status": "error", "message": "Gmail credentials not configured."}
            
            msg = MIMEMultipart()
            msg['From'] = GMAIL_USERNAME
            msg['To'] = to_email
            msg['Subject'] = subject
            if cc:
                msg['Cc'] = cc
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
            
            recipients = [to_email]
            if cc:
                recipients.extend(cc.split(','))
            
            server.sendmail(GMAIL_USERNAME, recipients, msg.as_string())
            server.quit()
            
            return {"status": "success", "message": f"Email sent successfully to {to_email}."}
        except Exception as e:
            return {"status": "error", "message": f"Failed to send email: {str(e)}"}
    
    def read_email(self, count=5, unread_only=True):
        """Read recent emails from Gmail"""
        try:
            if not GMAIL_USERNAME or not GMAIL_PASSWORD:
                return {"status": "error", "message": "Gmail credentials not configured."}
            
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(GMAIL_USERNAME, GMAIL_PASSWORD)
            mail.select('inbox')
            
            search_criteria = 'UNSEEN' if unread_only else 'ALL'
            status, messages = mail.search(None, search_criteria)
            email_ids = messages[0].split()
            
            recent_emails = []
            for email_id in email_ids[-count:]:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                subject, encoding = decode_header(email_message["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8')
                
                from_addr = email_message.get("From")
                
                recent_emails.append({
                    "from": from_addr,
                    "subject": subject,
                    "id": email_id.decode()
                })
            
            mail.close()
            mail.logout()
            
            return {"status": "success", "message": f"Retrieved {len(recent_emails)} emails.", "emails": recent_emails}
        except Exception as e:
            return {"status": "error", "message": f"Failed to read emails: {str(e)}"}
    
    def send_whatsapp(self, phone_number, message, delay=1):
        """Send WhatsApp message using pywhatkit"""
        try:
            import time as time_module
            current_time = time_module.localtime()
            hour = current_time.tm_hour
            minute = current_time.tm_min + delay
            
            if minute >= 60:
                hour += 1
                minute -= 60
            
            kit.sendwhatmsg(phone_number, message, hour, minute)
            return {"status": "success", "message": f"WhatsApp message scheduled to {phone_number}."}
        except Exception as e:
            return {"status": "error", "message": f"Failed to send WhatsApp message: {str(e)}"}
    
    def send_instagram_message(self, username, message):
        """Send Instagram DM (placeholder)"""
        try:
            return {"status": "info", "message": f"Instagram messaging to {username} requires additional setup."}
        except Exception as e:
            return {"status": "error", "message": f"Instagram messaging error: {str(e)}"}