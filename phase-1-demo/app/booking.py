"""Appointment booking and queue management logic."""

from datetime import datetime
from database import read_db, write_db, get_next_id
from typing import Dict, List, Any


def get_or_create_patient(phone: str, name: str = None) -> Dict[str, Any]:
    """Get existing patient or create new one.
    
    Args:
        phone: Patient phone number
        name: Patient name (optional)
    
    Returns:
        Patient dict
    """
    db = read_db()
    
    # Find existing patient
    for patient in db["patients"]:
        if patient["phone"] == phone:
            if name and not patient.get("name"):
                patient["name"] = name
                write_db(db)
            return patient
    
    # Create new patient
    patient = {
        "id": get_next_id("patients"),
        "phone": phone,
        "name": name or "Unknown",
        "created_at": datetime.utcnow().isoformat()
    }
    db["patients"].append(patient)
    write_db(db)
    
    print(f"✓ New patient created: {phone} ({name})")
    return patient


def generate_token() -> int:
    """Generate next available token number.
    
    Returns:
        Next token number
    """
    db = read_db()
    today = datetime.utcnow().date().isoformat()
    
    # Get max token from today's appointments
    today_tokens = [
        a["token"] for a in db["appointments"]
        if a["created_at"].startswith(today) and a["status"] == "booked"
    ]
    
    return (max(today_tokens) if today_tokens else 0) + 1


def create_appointment(patient_id: int, problem: str) -> Dict[str, Any]:
    """Create new appointment for patient.
    
    Args:
        patient_id: Patient ID
        problem: Medical problem/complaint
    
    Returns:
        Created Appointment dict
    """
    token = generate_token()
    
    db = read_db()
    appointment = {
        "id": get_next_id("appointments"),
        "patient_id": patient_id,
        "token": token,
        "problem": problem,
        "status": "booked",
        "created_at": datetime.utcnow().isoformat()
    }
    db["appointments"].append(appointment)
    write_db(db)
    
    print(f"✓ Appointment created: Token {token} for patient {patient_id}")
    return appointment


def check_duplicate_booking(phone: str) -> bool:
    """Check if patient already has a booking for today.
    
    Args:
        phone: Patient phone number
    
    Returns:
        True if patient has booking today, False otherwise
    """
    db = read_db()
    today = datetime.utcnow().date().isoformat()
    
    # Find patient
    patient = None
    for p in db["patients"]:
        if p["phone"] == phone:
            patient = p
            break
    
    if not patient:
        return False
    
    # Check for booking today
    for apt in db["appointments"]:
        if (
            apt["patient_id"] == patient["id"]
            and apt["created_at"].startswith(today)
            and apt["status"] == "booked"
        ):
            return True
    
    return False


def get_patient_appointment(phone: str) -> Dict[str, Any]:
    """Get today's appointment for patient.
    
    Args:
        phone: Patient phone number
    
    Returns:
        Appointment dict if found, None otherwise
    """
    db = read_db()
    today = datetime.utcnow().date().isoformat()
    
    # Find patient
    patient = None
    for p in db["patients"]:
        if p["phone"] == phone:
            patient = p
            break
    
    if not patient:
        return None
    
    # Find appointment
    for apt in db["appointments"]:
        if (
            apt["patient_id"] == patient["id"]
            and apt["created_at"].startswith(today)
            and apt["status"] == "booked"
        ):
            return apt
    
    return None


def get_current_token() -> int:
    """Get current token being served.
    
    Returns:
        Current token number or 1 if no appointments
    """
    db = read_db()
    today = datetime.utcnow().date().isoformat()
    
    # Get first booked appointment
    today_apts = [
        a for a in db["appointments"]
        if a["created_at"].startswith(today) and a["status"] == "booked"
    ]
    
    if not today_apts:
        return 1
    
    today_apts.sort(key=lambda x: x["token"])
    return today_apts[0]["token"]


def get_queue_position(phone: str) -> Dict[str, Any]:
    """Get position of patient in queue.
    
    Args:
        phone: Patient phone number
    
    Returns:
        Dictionary with queue info
    """
    appointment = get_patient_appointment(phone)
    
    if not appointment:
        return {
            "status": "error",
            "message": "No appointment found for today"
        }
    
    db = read_db()
    today = datetime.utcnow().date().isoformat()
    
    # Get current token
    current_token = get_current_token()
    your_token = appointment["token"]
    
    # Count patients ahead
    ahead = 0
    for apt in db["appointments"]:
        if (
            apt["created_at"].startswith(today)
            and apt["status"] == "booked"
            and apt["token"] < your_token
        ):
            ahead += 1
    
    # Estimate wait time (5 minutes per patient)
    estimated_minutes = ahead * 5
    
    if estimated_minutes == 0:
        estimated_wait = "Your turn!"
        position_msg = f"You are {your_token}st in queue"
    else:
        estimated_wait = f"{estimated_minutes} mins"
        position_msg = f"You are {your_token}th in queue ({ahead} ahead)"
    
    return {
        "status": "success",
        "current_token": current_token,
        "your_token": your_token,
        "position": your_token,
        "estimated_wait": estimated_wait,
        "total_ahead": ahead,
        "message": position_msg
    }


def get_all_appointments(status: str = None) -> List[Dict[str, Any]]:
    """Get all appointments (for doctor view).
    
    Args:
        status: Optional status filter
    
    Returns:
        List of appointment records with patient info
    """
    db = read_db()
    today = datetime.utcnow().date().isoformat()
    
    result = []
    for apt in db["appointments"]:
        if not apt["created_at"].startswith(today):
            continue
        
        if status and apt["status"] != status:
            continue
        
        # Find patient
        patient = next(
            (p for p in db["patients"] if p["id"] == apt["patient_id"]),
            None
        )
        
        result.append({
            "id": apt["id"],
            "token": apt["token"],
            "patient_name": patient["name"] if patient else "Unknown",
            "phone": patient["phone"] if patient else "Unknown",
            "problem": apt["problem"],
            "status": apt["status"],
            "created_at": apt["created_at"]
        })
    
    result.sort(key=lambda x: x["token"])
    return result
