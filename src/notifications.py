from typing import Dict, Any, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class NotificationSystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.smtp_username = config.get("smtp_username")
        self.smtp_password = config.get("smtp_password")
        self.notification_email = config.get("notification_email")
    
    async def send_notification(self, subject: str, content: str, recipients: List[str] = None):
        """Send email notification"""
        if not recipients:
            recipients = [self.notification_email]
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_username
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            
            msg.attach(MIMEText(content, "html"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Notification sent: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
    
    async def notify_bill_update(self, bill_data: Dict[str, Any]):
        """Notify about bill updates"""
        subject = f"Bill Update: {bill_data['title']}"
        content = f"""
        <h2>Bill Update Notification</h2>
        <p><strong>Title:</strong> {bill_data['title']}</p>
        <p><strong>Status:</strong> {bill_data.get('status', 'N/A')}</p>
        <p><strong>Last Action:</strong> {bill_data.get('last_action', 'N/A')}</p>
        <p><strong>Source:</strong> {bill_data['source']}</p>
        <p><strong>Updated At:</strong> {datetime.utcnow().isoformat()}</p>
        <p><a href="{bill_data.get('link', '#')}">View Bill Details</a></p>
        """
        await self.send_notification(subject, content)
    
    async def notify_new_document(self, doc_data: Dict[str, Any], bill_title: str):
        """Notify about new documents"""
        subject = f"New Document: {doc_data['title']}"
        content = f"""
        <h2>New Document Notification</h2>
        <p><strong>Bill:</strong> {bill_title}</p>
        <p><strong>Document:</strong> {doc_data['title']}</p>
        <p><strong>Type:</strong> {doc_data.get('document_type', 'N/A')}</p>
        <p><strong>Published:</strong> {doc_data.get('published_date', 'N/A')}</p>
        <p><a href="{doc_data['url']}">View Document</a></p>
        """
        await self.send_notification(subject, content)
    
    async def notify_error(self, tracker_name: str, error: str):
        """Notify about tracker errors"""
        subject = f"Tracker Error: {tracker_name}"
        content = f"""
        <h2>Tracker Error Notification</h2>
        <p><strong>Tracker:</strong> {tracker_name}</p>
        <p><strong>Error:</strong> {error}</p>
        <p><strong>Time:</strong> {datetime.utcnow().isoformat()}</p>
        """
        await self.send_notification(subject, content) 