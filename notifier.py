import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def send_email(subject, body):
    try:
        # Split RECEIVER_EMAIL by comma to get a list of recipients
        receiver_emails = [email.strip() for email in RECEIVER_EMAIL.split(",")]

        # Create the email message
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(receiver_emails)  # Join the list into a comma-separated string
        msg.set_content(body)

        # Connect to SMTP server and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)

        print(f"📧 Email sent to: {', '.join(receiver_emails)}")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
