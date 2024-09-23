import csv
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import dotenv

# Your Mailgun SMTP credentials
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
FROM_EMAIL = os.getenv('FROM_EMAIL')

event_name = '3108 CTF' # Update with your event name

# Log file to store failed emails
log_file_path = 'failed_emails.log'

# Function to send email with PDF attachment
def send_email(user_name, user_email, pdf_file_path):
    try:
        # Set up the email content
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = user_email
        msg['Subject'] = "E-SIJIL 3108 CTF"
        
        # Email body
        body = f"Salam sejahtera {user_name},\n\nTerima kasih kerana menyertai {event_name}\nSijil penyertaan anda dilampirkan bersama email ini."
        msg.attach(MIMEText(body, 'plain'))

        # Attach the PDF certificate
        with open(pdf_file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(pdf_file_path)}'
            )
            msg.attach(part)

        # Establish connection with Mailgun SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)  # Login with your credentials
        
        # Send email
        server.sendmail(FROM_EMAIL, user_email, msg.as_string())
        print(f"Email sent to {user_name} ({user_email}) successfully.")
        server.quit()  # Close the connection
        return True
    except Exception as e:
        print(f"Failed to send email to {user_name} ({user_email}). Error: {str(e)}")
        
        # Log the failed email
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"Failed to send email to {user_name} ({user_email}) - Error: {str(e)}\n")
        return False

# Function to read CSV and send emails with rate limiting
def send_emails_with_rate_limit(csv_file_path, batch_size=100, sleep_duration=3600):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        email_list = list(reader)
        
        total_emails = len(email_list)
        for i in range(0, total_emails, batch_size):
            # Send a batch of emails
            batch = email_list[i:i + batch_size]
            for row in batch:
                user_name = row['name']  # Adjusted to match CSV structure
                user_email = row['email']
                pdf_file_path = row['pdf_file']  # Path to the certificate PDF
                send_email(user_name, user_email, pdf_file_path)

            # If there are more emails to send, wait before sending the next batch
            if i + batch_size < total_emails:
                print(f"Sleeping for {sleep_duration/60} minutes to comply with rate limit...")
                time.sleep(sleep_duration)

# Specify the path to your generated CSV file with PDF paths
csv_file_path = 'output_with_pdf_paths.csv'

# Send emails with rate limit: 100 emails per hour
send_emails_with_rate_limit(csv_file_path, batch_size=100, sleep_duration=3600)
