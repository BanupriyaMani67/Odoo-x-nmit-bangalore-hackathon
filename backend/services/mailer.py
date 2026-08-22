
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_verification_email(to_email, token):
    client_url = os.environ.get('CLIENT_URL', 'http://localhost:5173')
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')

    verify_url = f'{client_url}/verify/{token}'

    html = f"""
      <div style="font-family:sans-serif;background:#472D30;color:#C9CBA3;padding:24px;border-radius:12px;">
        <h2 style="color:#FFE1A8;">Welcome to HRMS</h2>
        <p>Please verify your email address to activate your account.</p>
        <a href="{verify_url}" style="display:inline-block;padding:10px 20px;background:#E26D5C;color:#472D30;border-radius:8px;text-decoration:none;font-weight:bold;">
          Verify Email
        </a>
        <p style="margin-top:16px;font-size:12px;">Or copy this link: {verify_url}</p>
      </div>
    """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Verify your HRMS account'
    msg['From'] = f'"HRMS" <{gmail_user}>'
    msg['To'] = to_email
    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, [to_email], msg.as_string())
