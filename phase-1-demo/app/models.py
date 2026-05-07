"""SQLAlchemy ORM models for database tables."""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AppointmentStatus(str, enum.Enum):
    """Status of an appointment."""
    booked = "booked"
    completed = "completed"
    no_show = "no_show"
    cancelled = "cancelled"


class ConversationState(str, enum.Enum):
    """WhatsApp conversation states for state machine."""
    start = "start"
    menu = "menu"
    booking_name = "booking_name"
    booking_problem = "booking_problem"
    booking_confirm = "booking_confirm"
    check_status = "check_status"
    idle = "idle"


class Patient(Base):
    """Patient model - stores patient information."""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    whatsapp_state = relationship("WhatsAppState", back_populates="patient", uselist=False)
    otps = relationship("OTP", back_populates="patient")

    def __repr__(self):
        return f"<Patient(id={self.id}, phone={self.phone}, name={self.name})>"


class Appointment(Base):
    """Appointment model - stores booking information."""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    token = Column(Integer, unique=True, nullable=False, index=True)
    problem = Column(String(500), nullable=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.booked, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment(token={self.token}, patient_id={self.patient_id}, status={self.status})>"


class OTP(Base):
    """OTP model - stores one-time passwords."""
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="otps")

    def is_valid(self) -> bool:
        """Check if OTP is still valid (not expired)."""
        return datetime.utcnow() < self.expires_at

    def __repr__(self):
        return f"<OTP(phone={self.phone}, code={self.otp_code}, valid={self.is_valid()})>"


class WhatsAppState(Base):
    """WhatsApp conversation state - tracks multi-turn conversations."""
    __tablename__ = "whatsapp_states"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    state = Column(Enum(ConversationState), default=ConversationState.start, nullable=False)
    
    # Temporary storage during booking flow
    booking_name = Column(String(100), nullable=True)
    booking_problem = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="whatsapp_state")

    def __repr__(self):
        return f"<WhatsAppState(phone={self.phone}, state={self.state})>"
