import smtplib
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()


def send_email(filename='output.csv'):
    """
    Function to send an email with the job listings results.
    """
    # 1. Check if the required environment variables are set
    required_vars = ["EMAIL_SENDER", "EMAIL_RECEIVER",
                     "EMAIL_SMTP_HOST", "EMAIL_SMTP_PORT", "EMAIL_SENDER_PASSWORD"]
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Environment variable {var} is not set.")

    # 2. Get the current date and time for the email subject
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 3. Create MIMEMultipart Object
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Web Scraper Results - Job Listings from JobStreet - {now}"
    msg["From"] = os.getenv("EMAIL_SENDER")
    msg["To"] = os.getenv("EMAIL_RECEIVER")

    # 4. Create HTML Message
    html = f"""\
    <html>
    <body>
        <h1>Web Scraper Results</h1>
        <p>Here are the latest job listings as of ({now}) from JobStreet:</p>
    
        <p>Please find the attached CSV file for detailed results.</p>
    </body>
    </html>
    """

    part = MIMEText(html, "html")
    msg.attach(part)

    # 5. Add Attachment
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        msg.attach(part)

    # 6. Create SMTP Connection
    try:
        with smtplib.SMTP(os.getenv("EMAIL_SMTP_HOST"), os.getenv("EMAIL_SMTP_PORT")) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(os.getenv("EMAIL_SENDER"),
                         os.getenv("EMAIL_SENDER_PASSWORD"))
            print("Logged in to email server successfully.")
            server.sendmail(msg["From"], msg["To"], msg.as_string())
            print("Email sent successfully.")
            server.quit()
            print("SMTP connection closed.")
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Call the send_email function to send the email with the job listings results
    try:
        send_email()
    except Exception as e:
        print(f"Failed to send email: {e}")
