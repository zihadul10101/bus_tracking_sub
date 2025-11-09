import secrets
import datetime
from passlib.hash import sha256_crypt

def generate_otp():
    return str(secrets.randbelow(1000000)).zfill(6)

def send_otp(mobile, otp):
    # placeholder: integrate SMS provider
    print(f"Sending OTP {otp} to {mobile}")
    return True

def hash_password(password: str) -> str:
    return sha256_crypt.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return sha256_crypt.verify(password, hashed)
