"""WhatsApp chatbot integration and message handling."""

import json
import os
import requests
from database import read_db, write_db, get_next_id
from booking import get_or_create_patient, create_appointment, check_duplicate_booking, get_queue_position
from datetime import datetime
from typing import Dict, Any

WHATSAPP_API_URL = "https://graph.instagram.com/v18.0"
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")


def get_or_create_state(phone: str) -> Dict[str, Any]:
    """Get or create WhatsApp conversation state for phone.
    
    Args:
        phone: Phone number
    
    Returns:
        WhatsAppState dict
    """
    db = read_db()
    
    # Find existing state
    for state in db["whatsapp_states"]:
        if state["phone"] == phone:
            return state
    
    # Create new state
    state = {
        "id": get_next_id("whatsapp_states"),
        "phone": phone,
        "patient_id": None,
        "state": "start",
        "booking_name": None,
        "booking_problem": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    db["whatsapp_states"].append(state)
    write_db(db)
    
    return state


def update_state(phone: str, new_state: str, **kwargs):
    """Update conversation state and optional data.
    
    Args:
        phone: Phone number
        new_state: New conversation state
        **kwargs: Additional fields to update
    """
    db = read_db()
    
    # Find and update state
    for state in db["whatsapp_states"]:
        if state["phone"] == phone:
            state["state"] = new_state
            state["updated_at"] = datetime.utcnow().isoformat()
            
            for key, value in kwargs.items():
                if key in state:
                    state[key] = value
            
            write_db(db)
            return state
    
    # If not found, create new
    state = get_or_create_state(phone)
    state["state"] = new_state
    for key, value in kwargs.items():
        if key in state:
            state[key] = value
    update_state(phone, new_state, **kwargs)  # Recursive call to update


def send_whatsapp_message(phone: str, message: str) -> bool:
    """Send WhatsApp message via Meta API.
    
    Args:
        phone: Recipient phone number
        message: Message text
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not WHATSAPP_API_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print(f"⚠️  WhatsApp API not configured. Would send to {phone}: {message}")
        return True  # In demo, pretend it was sent
    
    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "text",
        "text": {"preview_url": False, "body": message}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✓ WhatsApp message sent to {phone}")
            return True
        else:
            print(f"❌ Failed to send WhatsApp message: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending WhatsApp message: {str(e)}")
        return False


def handle_incoming_message(phone: str, message_text: str) -> str:
    """Process incoming WhatsApp message and return response.
    
    Implements a multi-turn conversation state machine.
    
    Args:
        phone: Sender phone number
        message_text: Message content
    
    Returns:
        Response message to send back
    """
    print(f"\n📱 Message from {phone}: {message_text}")
    
    message_text = message_text.strip().lower()
    state = get_or_create_state(phone)
    current_state = state["state"]
    
    # ==================== START STATE ====================
    if current_state == "start":
        update_state(phone, "menu")
        response = (
            "🏥 Welcome to Clinic Queue Management!\n\n"
            "What would you like to do?\n"
            "1️⃣  Book Appointment\n"
            "2️⃣  Check Queue Status\n\n"
            "Reply with 1 or 2"
        )
        return response
    
    # ==================== MENU STATE ====================
    if current_state == "menu":
        if message_text == "1":
            update_state(phone, "booking_name")
            response = "📝 What is your name?"
            return response
        elif message_text == "2":
            result = get_queue_position(phone)
            if result["status"] == "error":
                response = f"❌ {result['message']}"
            else:
                response = (
                    f"📊 Your Queue Status:\n\n"
                    f"Your Token: {result['your_token']}\n"
                    f"Current Token: {result['current_token']}\n"
                    f"Position: {result['position']}\n"
                    f"Estimated Wait: {result['estimated_wait']}\n\n"
                    f"{result['message']}"
                )
            return response
        else:
            response = "❌ Invalid option. Please reply with 1 or 2"
            return response
    
    # ==================== BOOKING NAME STATE ====================
    if current_state == "booking_name":
        if len(message_text) < 2:
            response = "❌ Name too short. Please enter your full name:"
            return response
        
        update_state(phone, "booking_problem", booking_name=message_text.title())
        response = "🏥 What is your medical problem or complaint?"
        return response
    
    # ==================== BOOKING PROBLEM STATE ====================
    if current_state == "booking_problem":
        if len(message_text) < 3:
            response = "❌ Please describe your problem more clearly:"
            return response
        
        # Check for duplicate booking
        if check_duplicate_booking(phone):
            update_state(phone, "menu")
            response = (
                "❌ You already have an appointment today!\n\n"
                "What would you like to do next?\n"
                "1️⃣  Check Status\n"
                "2️⃣  Back to Menu"
            )
            return response
        
        update_state(phone, "booking_confirm", booking_problem=message_text.title())
        
        # Get updated state
        state = get_or_create_state(phone)
        response = (
            f"📋 Please confirm your booking:\n\n"
            f"Name: {state['booking_name']}\n"
            f"Problem: {state['booking_problem']}\n\n"
            f"Reply 'YES' to confirm or 'NO' to cancel"
        )
        return response
    
    # ==================== BOOKING CONFIRM STATE ====================
    if current_state == "booking_confirm":
        if message_text == "yes":
            # Create appointment
            patient = get_or_create_patient(phone, state["booking_name"])
            appointment = create_appointment(patient["id"], state["booking_problem"])
            
            # Reset state
            update_state(phone, "menu")
            
            response = (
                f"✅ Appointment Booked Successfully!\n\n"
                f"🎫 Your Token: {appointment['token']}\n"
                f"👤 Name: {state['booking_name']}\n"
                f"🏥 Problem: {state['booking_problem']}\n\n"
                f"Please arrive on time. Your token will be called soon.\n\n"
                f"What would you like to do next?\n"
                f"1️⃣  Book Another Appointment\n"
                f"2️⃣  Check Queue Status"
            )
            print(f"✓ Booking confirmed for {phone}")
            return response
        elif message_text == "no":
            update_state(phone, "menu")
            response = (
                "❌ Booking cancelled.\n\n"
                "What would you like to do?\n"
                "1️⃣  Book Appointment\n"
                "2️⃣  Check Queue Status"
            )
            return response
        else:
            response = "❓ Please reply 'YES' to confirm or 'NO' to cancel"
            return response
    
    # Default fallback
    update_state(phone, "menu")
    response = (
        "🏥 Welcome to Clinic Queue Management!\n\n"
        "What would you like to do?\n"
        "1️⃣  Book Appointment\n"
        "2️⃣  Check Queue Status"
    )
    return response


def verify_webhook_token(token: str) -> bool:
    """Verify WhatsApp webhook verification token.
    
    Args:
        token: Token from webhook request
    
    Returns:
        True if token matches, False otherwise
    """
    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "clinic_queue_verify_token_2026_secure")
    return token == expected_token
