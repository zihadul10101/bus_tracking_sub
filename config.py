# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # ← Loads .env file

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = "HS256"

# Email Settings (SMTP)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")  # App Password with spaces OK
APP_NAME = os.getenv("APP_NAME", "BUS APP")

# Optional: Resend (if you switch later)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")