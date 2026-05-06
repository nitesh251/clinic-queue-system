"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class AppointmentStatusEnum(str, Enum):
    """Appointment status enum for responses."""
    booked = "booked"
    completed = "completed"
    no_show = "no_show"
    cancelled = "cancelled"


# ==================== OTP Schemas ====================

class SendOTPRequest(BaseModel):
    """Request to send OTP to a phone number."""
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number (with country code)")

    @validator('phone')
    def validate_phone(cls, v):
        # Basic validation: contains only digits
        if not v.replace('+', '').isdigit():
            raise ValueError('Phone must contain only digits and optional + prefix')
        return v


class VerifyOTPRequest(BaseModel):
    """Request to verify OTP."""
    phone: str = Field(..., min_length=10, max_length=20)
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")

    @validator('otp')
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must be 6 digits')
        return v


class OTPResponse(BaseModel):
    """Response after OTP operations."""
    status: str = Field(..., description="success or error")
    message: str
    otp: Optional[str] = None  # Only in development mode


# ==================== Booking Schemas ====================

class BookingRequest(BaseModel):
    """Request to book an appointment."""
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    problem: str = Field(..., min_length=5, max_length=500)


class BookingResponse(BaseModel):
    """Response after booking appointment."""
    status: str
    token: int
    message: str
    patient_id: int


# ==================== Queue Schemas ====================

class QueueStatusResponse(BaseModel):
    """Response with queue status information."""
    status: str
    current_token: int
    your_token: int
    position: int
    estimated_wait: str
    total_ahead: int
    message: str


# ==================== Appointment Schemas ====================

class AppointmentDetailResponse(BaseModel):
    """Detailed appointment information."""
    id: int
    token: int
    patient_name: str
    phone: str
    problem: str
    status: AppointmentStatusEnum
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorDashboardResponse(BaseModel):
    """Doctor dashboard with all appointments."""
    status: str
    count: int
    appointments: List[AppointmentDetailResponse]


# ==================== Health Check ====================

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    message: str = "Clinic Queue System is running"
    version: str = "1.0.0"
