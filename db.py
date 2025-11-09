# db.py
from pymongo import MongoClient
import datetime

# DIRECT CONNECTION — NO config needed!
client = MongoClient("mongodb://localhost:27017/")
db = client["bus_app"]  # Your database name

# Auto-delete expired OTPs after 15 minutes
db.pending_users.create_index(
    "otp_expiry", 
    expireAfterSeconds=0
)

print("MongoDB Connected Successfully!")