from config import config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

async def send_verification_email(self, email: str, verification_token: str):
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'devinsightlemon@gmail.com'
        smtp_password = 'fvgj qctg bvmq zkva'

        verification_url = f"http://127.0.0.1:8000/verify-email?token={verification_token}"

        sender_email = smtp_username
        receiver_email = email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = 'Verify Your Email'

        html_body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #0077be;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #0077be;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 0.9em;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Verify Your Email</h1>
                <p>Hello,</p>
                <p>Thank you for signing up. Please click the button below to verify your email address:</p>
                <a href="{verification_url}" class="button">Verify Email</a>
                <p>If the button above doesn't work, you can also copy and paste the following link into your browser:</p>
                <p>{verification_url}</p>
                <p>Thank you,<br>Your Company Team</p>
            </div>
            <div class="footer">
                <p>This email was sent by Your Company. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """

        message.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"Verification email sent to {receiver_email}")
        except Exception as e:
            print(f"Failed to send verification email: {str(e)}")