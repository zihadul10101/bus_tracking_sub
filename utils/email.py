import resend
from config import RESEND_API_KEY, APP_NAME

# Set API key
resend.api_key ="9f8e6d5c4b3a291807f6e5d4c3b2a1908f7e6d5c4b3a291807f6e5d4c3b2a190"

print("RESEND v0.8.0 CONNECTED — EMAILS READY!")

def send_email(to_email, subject, html_body):
    try:
        resend.emails.send({
            "from": f"sub_bus <no-reply@resend.dev>",
            "to": to_email,
            "subject": subject,
            "html": html_body
        })
        print(f"EMAIL SENT TO {to_email}")
        return True
    except Exception as e:
        print(f"RESEND ERROR: {e}")
        return False


# OTP EMAIL
def send_otp_email(to_email, name, otp):
    subject = f"[{APP_NAME}] Your OTP Code"
    html = f"""
    <div style="font-family: Arial; text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px;">
        <h1>Welcome {name}!</h1>
        <p>Your verification code is:</p>
        <h2 style="font-size: 48px; letter-spacing: 10px; background: white; color: #667eea; padding: 20px; border-radius: 15px; display: inline-block;">
            {otp}
        </h2>
        <p><strong>Valid for 10 minutes</strong></p>
    </div>
    """
    send_email(to_email, subject, html)


# RESET PASSWORD EMAIL
def send_reset_email(to_email, name, reset_link):
    subject = f"[{APP_NAME}] Reset Your Password"
    html = f"""
    <div style="font-family: Arial; max-width: 500px; margin: 40px auto; padding: 30px; border: 1px solid #ddd; border-radius: 15px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
        <h2 style="color: #667eea;">Password Reset</h2>
        <p>Hello <strong>{name}</strong>,</p>
        <p>Click below to reset:</p>
        <a href="{reset_link}" style="background: #667eea; color: white; padding: 18px 40px; text-decoration: none; border-radius: 50px; font-size: 20px; font-weight: bold; display: inline-block; margin: 20px;">
            RESET PASSWORD
        </a>
        <p><small>Expires in 15 minutes</small></p>
        <hr>
        <small>{APP_NAME} Team</small>
    </div>
    """
    send_email(to_email, subject, html)