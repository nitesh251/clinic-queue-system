"""Main FastAPI application with all routes."""

from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime
import json

# Import database and services
from app.database import init_db, read_db
from app.otp import create_otp, verify_otp
from app.booking import (
    get_or_create_patient,
    create_appointment,
    check_duplicate_booking,
    get_queue_position,
    get_all_appointments,
)
from app.whatsapp import handle_incoming_message, verify_webhook_token, send_whatsapp_message

# Initialize FastAPI app
app = FastAPI(
    title="Clinic Queue Management System",
    description="Phase 1 Demo - Book appointments, track queue, WhatsApp integration",
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
    print("\n" + "="*60)
    print("🏥 Clinic Queue Management System - Phase 1 DEMO")
    print("="*60)
    init_db()
    print("✓ Database initialized")
    print("\n📍 API Endpoints:")
    print("   • Swagger UI: /docs")
    print("   • ReDoc: /redoc")
    print("   • Health: /health")
    print("\n🌐 Deployment:")
    print("   • Local: http://localhost:8000")
    print("   • Live: https://clinic-queue-system.onrender.com")
    print("="*60 + "\n")


# ==================== ROOT & HEALTH ====================

@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "Clinic Queue Management System",
        "version": "1.0.0",
        "phase": "1 - DEMO",
        "docs": "/docs",
        "status": "live",
        "endpoints": {
            "health": "/health",
            "auth": ["/send-otp", "/verify-otp"],
            "booking": ["/book"],
            "queue": ["/queue-status"],
            "doctor": ["/doctor/appointments"],
            "whatsapp": ["/webhook"],
            "testing": ["/test-whatsapp"]
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Clinic Queue System is running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== OTP ENDPOINTS ====================

@app.get("/send-otp")
def send_otp(phone: str = Query(..., description="Phone number with country code")):
    """Send OTP to phone number.
    
    Args:
        phone: Phone number (with country code)
    
    Returns:
        JSON with OTP (demo mode only)
    """
    try:
        otp_code = create_otp(phone)
        return {
            "status": "success",
            "message": f"OTP sent to {phone}",
            "otp": otp_code,  # Only in demo
            "expires_in_minutes": int(os.getenv("OTP_EXPIRY_MINUTES", 10))
        }
    except Exception as e:
        print(f"❌ Error sending OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/verify-otp")
def verify_otp_endpoint(phone: str = Query(...), otp: str = Query(..., min_length=6, max_length=6)):
    """Verify OTP code.
    
    Args:
        phone: Phone number
        otp: 6-digit OTP
    
    Returns:
        JSON with verification status
    """
    try:
        if verify_otp(phone, otp):
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

@app.get("/book")
def book_appointment(
    name: str = Query(..., min_length=2),
    phone: str = Query(...),
    problem: str = Query(..., min_length=5)
):
    """Book an appointment.
    
    Args:
        name: Patient name
        phone: Patient phone
        problem: Medical problem
    
    Returns:
        JSON with token and appointment details
    """
    try:
        # Check for duplicate booking
        if check_duplicate_booking(phone):
            raise HTTPException(
                status_code=400,
                detail="You already have an appointment for today"
            )
        
        # Create or get patient
        patient = get_or_create_patient(phone, name)
        
        # Create appointment
        appointment = create_appointment(patient["id"], problem)
        
        return {
            "status": "success",
            "token": appointment["token"],
            "message": f"✓ Appointment booked! Your token: {appointment['token']}",
            "patient_id": patient["id"],
            "appointment_id": appointment["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error booking appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== QUEUE ENDPOINTS ====================

@app.get("/queue-status")
def get_queue_status(phone: str = Query(...)):
    """Get queue status for a patient.
    
    Args:
        phone: Patient phone number
    
    Returns:
        JSON with queue position and wait time
    """
    try:
        result = get_queue_position(phone)
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting queue status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DOCTOR ENDPOINTS ====================

@app.get("/doctor/appointments")
def doctor_appointments():
    """Get all appointments (doctor dashboard).
    
    Returns:
        JSON with all appointments
    """
    try:
        appointments = get_all_appointments()
        return {
            "status": "success",
            "count": len(appointments),
            "timestamp": datetime.utcnow().isoformat(),
            "appointments": appointments
        }
    except Exception as e:
        print(f"❌ Error getting appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WHATSAPP WEBHOOK ====================

@app.get("/webhook")
def webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """WhatsApp webhook verification (GET request from Meta).
    
    Meta sends GET request to verify webhook endpoint.
    """
    try:
        if hub_mode == "subscribe" and verify_webhook_token(hub_token):
            print(f"✓ WhatsApp webhook verified")
            return int(hub_challenge)
        else:
            print(f"❌ Invalid webhook verification attempt")
            return {"status": "error", "message": "Invalid verification"}
    except Exception as e:
        print(f"❌ Error verifying webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook")
async def webhook_receive(request: Request):
    """WhatsApp webhook to receive messages (POST request from Meta).
    
    Meta sends incoming messages to this endpoint.
    """
    try:
        body = await request.json()
        print(f"\n📨 Webhook received: {json.dumps(body, indent=2)[:200]}...")
        
        # Extract message information
        try:
            messages = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [])
            
            if not messages:
                return {"status": "ok"}
            
            message = messages[0]
            phone = message.get("from")
            message_text = message.get("text", {}).get("body", "")
            
            if phone and message_text:
                # Process message
                response = handle_incoming_message(phone, message_text)
                print(f"✓ Response prepared for {phone}: {response[:50]}...")
                
                # Send response via WhatsApp API
                send_whatsapp_message(phone, response)
        
        except (IndexError, KeyError, TypeError) as e:
            print(f"⚠️  Webhook structure unexpected: {str(e)}")
        
        # Always return 200 to acknowledge receipt
        return {"status": "ok"}
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return {"status": "ok"}  # Still return ok to prevent Meta retries


# ==================== TESTING ENDPOINT ====================

@app.get("/test-whatsapp")
def test_whatsapp(phone: str = Query(...), message: str = Query(...)):
    """Test WhatsApp chatbot locally (for testing without real WhatsApp).
    
    Args:
        phone: Test phone number
        message: Test message
    
    Returns:
        Bot response
    """
    try:
        response = handle_incoming_message(phone, message)
        return {
            "status": "success",
            "phone": phone,
            "message": message,
            "response": response
        }
    except Exception as e:
        print(f"❌ Error testing WhatsApp: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
