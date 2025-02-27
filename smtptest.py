import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import sys

# Create an email-sending function
def send_email(to_email: str, subject: str, body: str) -> str:
    # Email configuration (replace with your SMTP server details)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "test@gmail.com"
    sender_password = "test1234"

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Send the email
    # with smtplib.SMTP(smtp_server, smtp_port) as server:
    #     server.starttls()
    #     server.login(sender_email, sender_password)
    #     server.send_message(message)
    
    return f"Email sent to {to_email} with subject: {subject}"

def main():

    content = """
    I have gathered the latest updates from Accenture's newsroom. Here is a summary of the key points:

    1. Accenture is launching new capabilities to enhance AI solutions with Google Cloud and Salesforce, aiming to supercharge growth and customer experiences.
    2. The company has invested in Voltron Data to leverage GPU technology for simplifying large-scale data processing.
    3. Accenture has formed a joint venture with INFRONEER Holdings to address infrastructure management in Japan.
    4. They are expanding personalized learning services with SAP and advancing cloud and AI adoption in Saudi Arabia with Google Cloud.
    5. Accenture is acquiring Staufen AG to boost operational excellence in manufacturing and supply chains.

    These initiatives highlight Accenture's commitment to driving digital transformation and innovation across various industries globally.
    """

    # Send the email
    result = send_email("babal@microsoft.com", "Accenture News Update", content)
    print(result)

if __name__ == "__main__":
    main()