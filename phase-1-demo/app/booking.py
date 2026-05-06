"""Appointment booking and queue management logic."""

from datetime import datetime
from sqlalchemy.orm import Session
from models import Patient, Appointment, AppointmentStatus
from sqlalchemy import func


def get_or_create_patient(db: Session, phone: str, name: str = None) -> Patient:
    """Get existing patient or create new one.
    
    Args:
        db: Database session
        phone: Patient phone number
        name: Patient name (optional, used on first creation)
    
    Returns:
        Patient object
    """
    patient = db.query(Patient).filter(Patient.phone == phone).first()
    
    if patient:
        # Update name if provided and not already set
        if name and not patient.name:
            patient.name = name
            db.commit()
            db.refresh(patient)
        return patient
    
    # Create new patient
    patient = Patient(phone=phone, name=name)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    print(f"✓ New patient created: {phone} ({name})")
    return patient


def generate_token(db: Session) -> int:
    """Generate next available token number.
    
    Generates sequential token starting from 1.
    
    Returns:
        Next token number
    """
    # Get max token from today's appointments
    max_token = db.query(func.max(Appointment.token)).filter(
        func.date(Appointment.created_at) == datetime.utcnow().date()
    ).scalar()
    
    return (max_token or 0) + 1


def create_appointment(db: Session, patient: Patient, problem: str) -> Appointment:
    """Create new appointment for patient.
    
    Args:
        db: Database session
        patient: Patient object
        problem: Medical problem/complaint
    
    Returns:
        Created Appointment object
    """
    token = generate_token(db)
    
    appointment = Appointment(
        patient_id=patient.id,
        token=token,
        problem=problem,
        status=AppointmentStatus.booked
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    print(f"✓ Appointment created: Token {token} for {patient.phone}")
    return appointment


def check_duplicate_booking(db: Session, phone: str) -> bool:
    """Check if patient already has a booking for today.
    
    Args:
        db: Database session
        phone: Patient phone number
    
    Returns:
        True if patient has booking today, False otherwise
    """
    today = datetime.utcnow().date()
    
    appointment = db.query(Appointment).join(Patient).filter(
        Patient.phone == phone,
        func.date(Appointment.created_at) == today,
        Appointment.status.in_([AppointmentStatus.booked])
    ).first()
    
    return appointment is not None


def get_patient_appointment(db: Session, phone: str) -> Appointment:
    """Get today's appointment for patient.
    
    Args:
        db: Database session
        phone: Patient phone number
    
    Returns:
        Appointment object if found, None otherwise
    """
    today = datetime.utcnow().date()
    
    appointment = db.query(Appointment).join(Patient).filter(
        Patient.phone == phone,
        func.date(Appointment.created_at) == today,
        Appointment.status == AppointmentStatus.booked
    ).first()
    
    return appointment


def get_current_token(db: Session) -> int:
    """Get current token being served.
    
    In demo, we assume first booked appointment is current.
    
    Returns:
        Current token number or 1 if no appointments
    """
    today = datetime.utcnow().date()
    
    # First booked appointment is current
    appointment = db.query(Appointment).filter(
        func.date(Appointment.created_at) == today,
        Appointment.status == AppointmentStatus.booked
    ).order_by(Appointment.token.asc()).first()
    
    return appointment.token if appointment else 1


def get_queue_position(db: Session, phone: str) -> dict:
    """Get position of patient in queue.
    
    Args:
        db: Database session
        phone: Patient phone number
    
    Returns:
        Dictionary with queue info
    """
    today = datetime.utcnow().date()
    
    # Get patient's appointment
    appointment = db.query(Appointment).join(Patient).filter(
        Patient.phone == phone,
        func.date(Appointment.created_at) == today,
        Appointment.status == AppointmentStatus.booked
    ).first()
    
    if not appointment:
        return {
            "status": "error",
            "message": "No appointment found for today"
        }
    
    # Get current token
    current_token = get_current_token(db)
    your_token = appointment.token
    
    # Count patients ahead
    ahead = db.query(func.count(Appointment.id)).filter(
        func.date(Appointment.created_at) == today,
        Appointment.status == AppointmentStatus.booked,
        Appointment.token < your_token
    ).scalar()
    
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


def get_all_appointments(db: Session, status: str = None):
    """Get all appointments (for doctor view).
    
    Args:
        db: Database session
        status: Optional status filter (booked, completed, no_show, cancelled)
    
    Returns:
        List of appointment records with patient info
    """
    today = datetime.utcnow().date()
    
    query = db.query(Appointment).join(Patient).filter(
        func.date(Appointment.created_at) == today
    )
    
    if status:
        query = query.filter(Appointment.status == status)
    
    appointments = query.order_by(Appointment.token.asc()).all()
    
    result = []
    for apt in appointments:
        result.append({
            "id": apt.id,
            "token": apt.token,
            "patient_name": apt.patient.name or "Unknown",
            "phone": apt.patient.phone,
            "problem": apt.problem,
            "status": apt.status.value,
            "created_at": apt.created_at.isoformat()
        })
    
    return result
