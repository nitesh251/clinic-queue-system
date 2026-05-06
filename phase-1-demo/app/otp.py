"""OTP generation and verification logic."""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import OTP
import os

OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))
OTP_LENGTH = int(os.getenv("OTP_LENGTH", "6"))


def generate_otp() -> str:
    """Generate a random 6-digit OTP."""
    return ''.join([str(random.randint(0, 9)) for _ in range(OTP_LENGTH)])


def create_otp(db: Session, phone: str) -> str:
    """Create and store OTP in database.
    
    Args:
        db: Database session
        phone: Phone number to send OTP to
    
    Returns:
        Generated OTP code
    """
    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    # Create OTP record
    otp_record = OTP(
        phone=phone,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)
    
    # Print to console (demo mode)
    print(f"\n📱 OTP for {phone}: {otp_code}")
    print(f"   Expires at: {expires_at}\n")
    
    return otp_code


def verify_otp(db: Session, phone: str, otp_code: str) -> bool:
    """Verify OTP and return True if valid.
    
    Args:
        db: Database session
        phone: Phone number to verify
        otp_code: OTP code to check
    
    Returns:
        True if OTP is valid and not expired, False otherwise
    """
    # Get latest OTP for phone
    otp = db.query(OTP).filter(
        OTP.phone == phone,
        OTP.otp_code == otp_code
    ).order_by(OTP.created_at.desc()).first()
    
    if not otp:
        print(f"❌ OTP not found for {phone}")
        return False
    
    if not otp.is_valid():
        print(f"❌ OTP expired for {phone}")
        return False
    
    print(f"✓ OTP verified for {phone}")
    return True


def get_valid_otp(db: Session, phone: str) -> OTP:
    """Get the latest valid OTP for a phone number.
    
    Args:
        db: Database session
        phone: Phone number
    
    Returns:
        OTP object if valid OTP exists, None otherwise
    """
    otp = db.query(OTP).filter(
        OTP.phone == phone
    ).order_by(OTP.created_at.desc()).first()
    
    if otp and otp.is_valid():
        return otp
    return None
