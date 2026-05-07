"""JSON file-based database for Phase 1 demo."""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

DATA_FILE = "clinic_data.json"


def init_db():
    """Initialize database file if it doesn't exist."""
    if not os.path.exists(DATA_FILE):
        default_data = {
            "patients": [],
            "appointments": [],
            "otps": [],
            "whatsapp_states": []
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(default_data, f, indent=2)
        print(f"✓ Database file created: {DATA_FILE}")
    else:
        print(f"✓ Database file exists: {DATA_FILE}")


def read_db() -> Dict[str, Any]:
    """Read entire database."""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return {
            "patients": [],
            "appointments": [],
            "otps": [],
            "whatsapp_states": []
        }


def write_db(data: Dict[str, Any]):
    """Write entire database."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"❌ Error writing database: {e}")


def get_next_id(collection: str) -> int:
    """Get next ID for a collection."""
    db = read_db()
    items = db.get(collection, [])
    if not items:
        return 1
    return max(item.get('id', 0) for item in items) + 1
