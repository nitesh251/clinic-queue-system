"""OTP generation and verification logic."""

import random
from datetime import datetime, timedelta
from app.database import read_db, write_db, get_next_id
import os

OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))
OTP_LENGTH = int(os.getenv("OTP_LENGTH", "6"))


def generate_otp() -> str:
    """Generate a random 6-digit OTP."""
    return ''.join([str(random.randint(0, 9)) for _ in range(OTP_LENGTH)])


def create_otp(phone: str) -> str:
    """Create and store OTP in database.
    
    Args:
        phone: Phone number to send OTP to
    
    Returns:
        Generated OTP code
    """
    otp_code = generate_otp()
    expires_at = (datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat()
    
    db = read_db()
    otp_record = {
        "id": get_next_id("otps"),
        "phone": phone,
        "otp_code": otp_code,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at
    }
    db["otps"].append(otp_record)
    write_db(db)
    
    # Print to console (demo mode)
    print(f"\n📱 OTP for {phone}: {otp_code}")
    print(f"   Expires at: {expires_at}\n")
    
    return otp_code


def verify_otp(phone: str, otp_code: str) -> bool:
    """Verify OTP and return True if valid.
    
    Args:
        phone: Phone number to verify
        otp_code: OTP code to check
    
    Returns:
        True if OTP is valid and not expired, False otherwise
    """
    db = read_db()
    
    # Get latest OTP for phone
    otps = [o for o in db["otps"] if o["phone"] == phone]
    if not otps:
        print(f"❌ OTP not found for {phone}")
        return False
    
    otp = otps[-1]  # Get latest
    
    if otp["otp_code"] != otp_code:
        print(f"❌ OTP mismatch for {phone}")
        return False
    
    # Check expiry
    expires_at = datetime.fromisoformat(otp["expires_at"])
    if datetime.utcnow() > expires_at:
        print(f"❌ OTP expired for {phone}")
        return False
    
    print(f"✓ OTP verified for {phone}")
    return True
