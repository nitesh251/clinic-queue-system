"""Main FastAPI application with all routes."""

from fastapi import FastAPI, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

# Import database and models
from database import init_db, get_db, Base, engine
from models import Patient, Appointment, AppointmentStatus

# Import schemas
from schemas import (
    SendOTPRequest,
    VerifyOTPRequest,
    OTPResponse,
    BookingRequest,
    BookingResponse,
    QueueStatusResponse,
    DoctorDashboardResponse,
    HealthCheckResponse,
)

# Import services
from otp import create_otp, verify_otp
from booking import (
    get_or_create_patient,
    create_appointment,
    check_duplicate_booking,
    get_queue_position,
    get_all_appointments,
)
from whatsapp import handle_incoming_message, verify_webhook_token

# Initialize FastAPI app
app = FastAPI(
    title="Clinic Queue Management System",
    description="Demo - Phase 1: Book appointments, track queue, WhatsApp integration",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup():
    """Initialize database on app startup."""
    print("\n" + "="*50)
    print("🏥 Clinic Queue Management System - Phase 1")
    print("="*50)
    init_db()
    print("🚀 Application started")
    print("📖 API Docs: http://localhost:8000/docs")
    print("="*50 + "\n")


# ==================== HEALTH CHECK ====================

@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Clinic Queue System is running",
        "version": "1.0.0"
    }


# ==================== OTP ENDPOINTS ====================

@app.post("/send-otp", response_model=OTPResponse)
def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """Send OTP to phone number.
    
    Args:
        request: SendOTPRequest with phone number
        db: Database session
    
    Returns:
        OTPResponse with status and message
    """
    try:
        otp_code = create_otp(db, request.phone)
        return {
            "status": "success",
            "message": f"OTP sent to {request.phone}",
            "otp": otp_code  # Only in development
        }
    except Exception as e:
        print(f"❌ Error sending OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify-otp", response_model=OTPResponse)
def verify_otp_endpoint(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP code.
    
    Args:
        request: VerifyOTPRequest with phone and OTP
        db: Database session
    
    Returns:
        OTPResponse with verification status
    """
    try:
        if verify_otp(db, request.phone, request.otp):
            return {
                "status": "success",
                "message": "OTP verified successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    except Exception as e:
        print(f"❌ Error verifying OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== BOOKING ENDPOINTS ====================

@app.post("/book", response_model=BookingResponse)
def book_appointment(request: BookingRequest, db: Session = Depends(get_db)):
    """Book an appointment.
    
    Args:
        request: BookingRequest with name, phone, problem
        db: Database session
    
    Returns:
        BookingResponse with token and status
    """
    try:
        # Check for duplicate booking
        if check_duplicate_booking(db, request.phone):
            raise HTTPException(
                status_code=400,
                detail="You already have an appointment for today"
            )
        
        # Create or get patient
        patient = get_or_create_patient(db, request.phone, request.name)
        
        # Create appointment
        appointment = create_appointment(db, patient, request.problem)
        
        return {
            "status": "success",
            "token": appointment.token,
            "message": f"✓ Appointment booked! Your token: {appointment.token}",
            "patient_id": patient.id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error booking appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== QUEUE ENDPOINTS ====================

@app.get("/queue-status", response_model=QueueStatusResponse)
def get_queue_status(phone: str = Query(...), db: Session = Depends(get_db)):
    """Get queue status for a patient.
    
    Args:
        phone: Patient phone number
        db: Database session
    
    Returns:
        QueueStatusResponse with position and wait time
    """
    try:
        result = get_queue_position(db, phone)
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting queue status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DOCTOR ENDPOINTS ====================

@app.get("/doctor/appointments", response_model=DoctorDashboardResponse)
def doctor_appointments(db: Session = Depends(get_db)):
    """Get all appointments (doctor dashboard).
    
    Args:
        db: Database session
    
    Returns:
        DoctorDashboardResponse with all appointments
    """
    try:
        appointments = get_all_appointments(db)
        return {
            "status": "success",
            "count": len(appointments),
            "appointments": appointments
        }
    except Exception as e:
        print(f"❌ Error getting appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WHATSAPP WEBHOOK ====================

@app.get("/webhook")
def webhook_verify(request: Request):
    """WhatsApp webhook verification (GET request).
    
    Meta sends GET request with hub_mode, hub_verify_token, hub_challenge.
    """
    try:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        if mode == "subscribe" and verify_webhook_token(token):
            print(f"✓ WhatsApp webhook verified")
            return int(challenge)
        else:
            print(f"❌ Invalid webhook verification attempt")
            return {"status": "error", "message": "Invalid verification"}
    except Exception as e:
        print(f"❌ Error verifying webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook")
async def webhook_receive(request: Request, db: Session = Depends(get_db)):
    """WhatsApp webhook to receive messages (POST request).
    
    Meta sends incoming messages to this endpoint.
    """
    try:
        body = await request.json()
        
        # Log incoming webhook
        print(f"\n📨 Webhook received: {body}")
        
        # Extract message information
        # Expected structure: body['entry'][0]['changes'][0]['value']['messages'][0]
        try:
            messages = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [])
            
            if not messages:
                return {"status": "ok"}
            
            message = messages[0]
            phone = message.get("from")
            message_text = message.get("text", {}).get("body", "")
            
            if phone and message_text:
                # Process message and get response
                response = handle_incoming_message(db, phone, message_text)
                
                # In production, send response via WhatsApp API
                # For demo, just log it
                print(f"✓ Response prepared: {response[:50]}...")
                
        except (IndexError, KeyError, TypeError) as e:
            print(f"⚠️  Webhook structure unexpected: {str(e)}")
        
        # Always return 200 to acknowledge receipt
        return {"status": "ok"}
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return {"status": "ok"}  # Still return ok to prevent retries


# ==================== ROOT ENDPOINT ====================

@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "Clinic Queue Management System",
        "version": "1.0.0",
        "phase": "1 - DEMO",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": ["/send-otp", "/verify-otp"],
            "booking": ["/book"],
            "queue": ["/queue-status"],
            "doctor": ["/doctor/appointments"],
            "whatsapp": ["/webhook"]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
