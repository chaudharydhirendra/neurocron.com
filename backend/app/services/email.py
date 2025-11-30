"""
NeuroCron Email Service
Transactional email handling using SendGrid
"""

from typing import Optional, List, Dict, Any
import httpx
import logging
from jinja2 import Environment, BaseLoader

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending transactional emails.
    
    Uses SendGrid in production, logs in development.
    """
    
    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = settings.FROM_EMAIL
        self.api_url = "https://api.sendgrid.com/v3/mail/send"
        
        # Jinja2 for templates
        self.template_env = Environment(loader=BaseLoader())
    
    async def send(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_name: str = "NeuroCron",
    ) -> bool:
        """
        Send an email.
        
        Returns True if sent successfully, False otherwise.
        """
        if not self.api_key:
            # Log in development mode
            logger.info(f"[DEV EMAIL] To: {to_email}, Subject: {subject}")
            return True
        
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": self.from_email, "name": from_name},
            "subject": subject,
            "content": [
                {"type": "text/html", "value": html_content},
            ],
        }
        
        if text_content:
            payload["content"].insert(0, {"type": "text/plain", "value": text_content})
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_welcome(self, to_email: str, name: str) -> bool:
        """Send welcome email to new users."""
        subject = "Welcome to NeuroCron! 🧠"
        html = WELCOME_EMAIL_TEMPLATE.format(name=name)
        return await self.send(to_email, subject, html)
    
    async def send_password_reset(self, to_email: str, reset_url: str) -> bool:
        """Send password reset email."""
        subject = "Reset Your NeuroCron Password"
        html = PASSWORD_RESET_TEMPLATE.format(reset_url=reset_url)
        return await self.send(to_email, subject, html)
    
    async def send_verification(self, to_email: str, verification_url: str) -> bool:
        """Send email verification."""
        subject = "Verify Your NeuroCron Email"
        html = VERIFICATION_EMAIL_TEMPLATE.format(verification_url=verification_url)
        return await self.send(to_email, subject, html)
    
    async def send_campaign_alert(
        self,
        to_email: str,
        campaign_name: str,
        alert_type: str,
        message: str,
    ) -> bool:
        """Send campaign performance alert."""
        subject = f"Campaign Alert: {campaign_name}"
        html = CAMPAIGN_ALERT_TEMPLATE.format(
            campaign_name=campaign_name,
            alert_type=alert_type,
            message=message,
        )
        return await self.send(to_email, subject, html)
    
    async def send_weekly_report(
        self,
        to_email: str,
        report_data: Dict[str, Any],
    ) -> bool:
        """Send weekly performance report."""
        subject = "Your Weekly NeuroCron Report 📊"
        html = WEEKLY_REPORT_TEMPLATE.format(**report_data)
        return await self.send(to_email, subject, html)


# Email templates

WELCOME_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to NeuroCron</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #0A0A0F; color: #ffffff; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .logo {{ width: 60px; height: 60px; background: linear-gradient(135deg, #0066FF, #8B5CF6); border-radius: 16px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; }}
        .card {{ background: #1A1A24; border-radius: 16px; padding: 32px; margin-bottom: 24px; }}
        h1 {{ font-size: 28px; margin: 0 0 16px; }}
        p {{ color: rgba(255,255,255,0.7); line-height: 1.6; margin: 0 0 16px; }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #0066FF, #8B5CF6); color: white; text-decoration: none; padding: 14px 28px; border-radius: 12px; font-weight: 600; }}
        .features {{ display: grid; gap: 16px; }}
        .feature {{ display: flex; align-items: flex-start; gap: 12px; }}
        .feature-icon {{ width: 24px; height: 24px; background: rgba(0,102,255,0.1); border-radius: 8px; color: #0066FF; text-align: center; line-height: 24px; }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.4); font-size: 14px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🧠</div>
            <h1>Welcome to NeuroCron!</h1>
            <p>The Autonomous Marketing Brain</p>
        </div>
        
        <div class="card">
            <p>Hi {name},</p>
            <p>Welcome to NeuroCron! You've just joined the future of autonomous marketing. We're thrilled to have you on board.</p>
            <p>Here's what you can do now:</p>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🚀</div>
                    <div>
                        <strong>Create your first campaign</strong>
                        <p style="margin: 4px 0 0; font-size: 14px;">Let our AI help you build a complete marketing strategy.</p>
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔗</div>
                    <div>
                        <strong>Connect your platforms</strong>
                        <p style="margin: 4px 0 0; font-size: 14px;">Link Google Ads, Meta, and more for unified management.</p>
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-icon">💬</div>
                    <div>
                        <strong>Chat with NeuroCopilot</strong>
                        <p style="margin: 4px 0 0; font-size: 14px;">Ask anything about your marketing—we'll handle the rest.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div style="text-align: center;">
            <a href="https://neurocron.com/dashboard" class="btn">Go to Dashboard →</a>
        </div>
        
        <div class="footer">
            <p>NeuroCron - The Autonomous Marketing Brain</p>
            <p>© 2024 NeuroCron. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

PASSWORD_RESET_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #0A0A0F; color: #ffffff; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
        .card {{ background: #1A1A24; border-radius: 16px; padding: 32px; text-align: center; }}
        h1 {{ font-size: 24px; margin: 0 0 16px; }}
        p {{ color: rgba(255,255,255,0.7); line-height: 1.6; margin: 0 0 24px; }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #0066FF, #8B5CF6); color: white; text-decoration: none; padding: 14px 28px; border-radius: 12px; font-weight: 600; }}
        .note {{ font-size: 14px; color: rgba(255,255,255,0.4); margin-top: 24px; }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.4); font-size: 14px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Reset Your Password</h1>
            <p>We received a request to reset your NeuroCron password. Click the button below to create a new password.</p>
            <a href="{reset_url}" class="btn">Reset Password</a>
            <p class="note">This link will expire in 1 hour. If you didn't request this, you can safely ignore this email.</p>
        </div>
        <div class="footer">
            <p>NeuroCron - The Autonomous Marketing Brain</p>
        </div>
    </div>
</body>
</html>
"""

VERIFICATION_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Email</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #0A0A0F; color: #ffffff; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
        .card {{ background: #1A1A24; border-radius: 16px; padding: 32px; text-align: center; }}
        h1 {{ font-size: 24px; margin: 0 0 16px; }}
        p {{ color: rgba(255,255,255,0.7); line-height: 1.6; margin: 0 0 24px; }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #0066FF, #8B5CF6); color: white; text-decoration: none; padding: 14px 28px; border-radius: 12px; font-weight: 600; }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.4); font-size: 14px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Verify Your Email</h1>
            <p>Please verify your email address to complete your NeuroCron registration.</p>
            <a href="{verification_url}" class="btn">Verify Email</a>
        </div>
        <div class="footer">
            <p>NeuroCron - The Autonomous Marketing Brain</p>
        </div>
    </div>
</body>
</html>
"""

CAMPAIGN_ALERT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campaign Alert</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #0A0A0F; color: #ffffff; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
        .card {{ background: #1A1A24; border-radius: 16px; padding: 32px; }}
        h1 {{ font-size: 24px; margin: 0 0 16px; }}
        p {{ color: rgba(255,255,255,0.7); line-height: 1.6; margin: 0 0 16px; }}
        .alert-box {{ background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 16px; margin: 16px 0; }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #0066FF, #8B5CF6); color: white; text-decoration: none; padding: 14px 28px; border-radius: 12px; font-weight: 600; }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.4); font-size: 14px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🚨 Campaign Alert</h1>
            <p><strong>Campaign:</strong> {campaign_name}</p>
            <p><strong>Alert Type:</strong> {alert_type}</p>
            <div class="alert-box">
                <p style="margin: 0;">{message}</p>
            </div>
            <a href="https://neurocron.com/dashboard/campaigns" class="btn">View Campaign</a>
        </div>
        <div class="footer">
            <p>NeuroCron - The Autonomous Marketing Brain</p>
        </div>
    </div>
</body>
</html>
"""

WEEKLY_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #0A0A0F; color: #ffffff; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
        .card {{ background: #1A1A24; border-radius: 16px; padding: 32px; margin-bottom: 24px; }}
        h1 {{ font-size: 28px; margin: 0 0 16px; text-align: center; }}
        h2 {{ font-size: 18px; margin: 0 0 16px; }}
        p {{ color: rgba(255,255,255,0.7); line-height: 1.6; margin: 0 0 16px; }}
        .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
        .stat {{ background: rgba(255,255,255,0.05); border-radius: 12px; padding: 16px; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #0066FF; }}
        .stat-label {{ font-size: 14px; color: rgba(255,255,255,0.5); }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #0066FF, #8B5CF6); color: white; text-decoration: none; padding: 14px 28px; border-radius: 12px; font-weight: 600; }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.4); font-size: 14px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Your Weekly Report</h1>
        
        <div class="card">
            <h2>Performance Summary</h2>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_spend}</div>
                    <div class="stat-label">Total Spend</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{total_revenue}</div>
                    <div class="stat-label">Revenue</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{total_conversions}</div>
                    <div class="stat-label">Conversions</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{roas}</div>
                    <div class="stat-label">ROAS</div>
                </div>
            </div>
        </div>
        
        <div style="text-align: center;">
            <a href="https://neurocron.com/analytics" class="btn">View Full Report</a>
        </div>
        
        <div class="footer">
            <p>NeuroCron - The Autonomous Marketing Brain</p>
        </div>
    </div>
</body>
</html>
"""

# Singleton instance
email_service = EmailService()

