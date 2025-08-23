import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart # Import MIMEMultipart for proper email construction
from app.core.config import settings

def send_email(to_email: str, subject: str, body: str) -> None:
    # Check if necessary email settings are configured
    if not settings.MAIL_SERVER or not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        print(f"[EMAIL-DEBUG] Email not configured. To: {to_email}\nSubject: {subject}\n\n{body}")
        return

    # Create a MIMEText object for the email body
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = settings.MAIL_FROM # Corrected: Use MAIL_FROM
    msg['To'] = to_email
    msg.attach(MIMEText(body, 'plain')) # Attach the plain text body

    try:
        # Establish SMTP connection
        # Corrected: Use MAIL_SERVER and MAIL_PORT
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as s:
            # Start TLS encryption if enabled in settings
            if settings.MAIL_STARTTLS: # Check for MAIL_STARTTLS setting
                s.starttls()
            # Login to the SMTP server
            # Corrected: Use MAIL_USERNAME and MAIL_PASSWORD
            s.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            # Send the email
            s.sendmail(settings.MAIL_FROM, [to_email], msg.as_string())
            print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
