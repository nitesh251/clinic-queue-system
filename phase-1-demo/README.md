# 🏥 Clinic Queue Management System - PHASE 1 DEMO

A fully working, **completely FREE** clinic appointment and queue management system with **REAL WhatsApp integration**. Deploy in minutes, use immediately.

---

## ⚡ What You Get

### ✅ Working Features
- **OTP Authentication**: 6-digit code, 10-min expiry (printed to console in demo)
- **Appointment Booking**: Patients can book with name, phone, and problem
- **Real-time Queue**: See current token, your position, and estimated wait time
- **WhatsApp Chatbot**: Guided booking and status check via real WhatsApp Business Account
- **Doctor Dashboard**: View all bookings and appointments
- **JSON Database**: File-based, zero configuration needed

### ✅ Production Ready
- Clean, modular code
- Error handling and logging
- Environment-based configuration
- Ready to scale (Phase 2)

### ✅ FREE to Deploy & Use
- **Render**: Free hosting with auto HTTPS
- **WhatsApp Cloud API**: Free test mode
- **Zero cost** until you need paid features

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/nitesh251/clinic-queue-system.git
cd clinic-queue-system/phase-1-demo
```

### Step 2: Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies (FAST - No C++ Needed!)
```bash
pip install -r requirements.txt
```
✅ **No build errors, no compilation!**

### Step 4: Configure (Optional - Skip for Testing)
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your WhatsApp credentials (see section below)
# For now, you can leave defaults and test locally
```

### Step 5: Run!
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Server running at**: `http://localhost:8000`

---

## 🧪 Test It NOW (No WhatsApp Needed)

### Interactive API Docs
Visit: `http://localhost:8000/docs`

You'll see **Swagger UI** with all endpoints and "Try It Out" buttons.

### Test via cURL

#### 1. Health Check
```bash
curl http://localhost:8000/health
```

#### 2. Send OTP
```bash
curl "http://localhost:8000/send-otp?phone=919876543210"

# Response (demo shows OTP):
# {"status":"success","otp":"123456"}
```

#### 3. Verify OTP
```bash
curl "http://localhost:8000/verify-otp?phone=919876543210&otp=123456"
```

#### 4. Book Appointment
```bash
curl "http://localhost:8000/book?name=John+Doe&phone=919876543210&problem=Fever"

# Response:
# {"status":"success","token":1,"message":"Appointment booked!"}
```

#### 5. Check Queue Status
```bash
curl "http://localhost:8000/queue-status?phone=919876543210"
```

#### 6. Doctor Dashboard
```bash
curl http://localhost:8000/doctor/appointments
```

#### 7. Test WhatsApp Chatbot (Local)
```bash
curl "http://localhost:8000/test-whatsapp?phone=919876543210&message=Hi"
curl "http://localhost:8000/test-whatsapp?phone=919876543210&message=1"
curl "http://localhost:8000/test-whatsapp?phone=919876543210&message=John+Doe"
curl "http://localhost:8000/test-whatsapp?phone=919876543210&message=Fever"
curl "http://localhost:8000/test-whatsapp?phone=919876543210&message=YES"
```

---

## 📱 **REAL WhatsApp Integration** (Step-by-Step)

### Step 1: Create Meta Developer App

1. Go to: https://developers.facebook.com
2. Click **My Apps** → **Create App**
3. Fill in:
   - **App Name**: `Clinic Queue System`
   - **App Purpose**: `Business`
4. Click **Create App**

### Step 2: Add WhatsApp Product

1. In app dashboard → **Products**
2. Click **+ Add Product**
3. Search "WhatsApp"
4. Click **Set Up**
5. Choose **WhatsApp Business Account**

### Step 3: Get Your API Credentials

Go to: **Your App → WhatsApp → API Setup**

Copy these 3 values:

| Value | Where to Find |
|-------|---------------|
| **WHATSAPP_PHONE_NUMBER_ID** | API Setup → Step 1 → Phone Number section |
| **WHATSAPP_BUSINESS_ACCOUNT_ID** | API Setup → Business Account ID |
| **WHATSAPP_API_TOKEN** | Settings (left) → User Tokens → Generate Token |

### Step 4: Update .env File

Edit `.env` in your `phase-1-demo/` directory:

```env
# Your actual credentials from Meta
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_BUSINESS_ACCOUNT_ID=987654321098765
WHATSAPP_API_TOKEN=EAABs4cZ1234567890abcdefghijklmnop...
WHATSAPP_VERIFY_TOKEN=clinic_queue_verify_token_2026_secure

# Other settings (leave as is)
FASTAPI_ENV=development
DEBUG=True
OTP_EXPIRY_MINUTES=10
OTP_LENGTH=6
HOST=0.0.0.0
PORT=8000
```

### Step 5: Add Your Phone as Test Recipient

1. Go to: **Your App → WhatsApp → Getting Started**
2. Scroll to **"To send a test message to a customer"**
3. Add your phone number:
   ```
   +91 9876543210  (India)
   +1 2025551234   (USA)
   ```
4. Click **Send Test Message**
5. Check WhatsApp on your phone - you'll get a message! ✅

### Step 6: Test Locally with ngrok

For local testing, you need a public URL:

```bash
# Install: https://ngrok.com/download
# Sign up: https://ngrok.com/signup

# In a new terminal, run:
ngrok http 8000

# You'll get: https://xxxx-xx-xxx.ngrok.io
```

Then in Meta Dashboard:
- **WhatsApp → Configuration**
- **Webhook URL**: `https://xxxx-xx-xxx.ngrok.io/webhook`
- **Verify Token**: `clinic_queue_verify_token_2026_secure`
- Click **Save**

Meta will verify. If you see ✅ green checkmark, you're good!

### Step 7: Test Real WhatsApp

Send a message from your phone to your business number:

```
Message: Hi
```

Bot replies with menu! 🤖✅

---

## 🌐 Deploy to Render (FREE - 5 Minutes)

### Step 1: Push to GitHub
Code is already pushed ✅

### Step 2: Create Render Account
- Go to: https://render.com
- Sign up with GitHub
- Connect your GitHub account

### Step 3: Create Web Service

1. Click **New +** → **Web Service**
2. Select `clinic-queue-system` repository
3. Configure:

| Field | Value |
|-------|-------|
| **Name** | `clinic-queue-system` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r phase-1-demo/requirements.txt` |
| **Start Command** | `cd phase-1-demo && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| **Instance Type** | `Free` |

### Step 4: Add Environment Variables

Click **Environment** and add:

```
FASTAPI_ENV=production
DEBUG=False
WHATSAPP_PHONE_NUMBER_ID=YOUR_ID
WHATSAPP_BUSINESS_ACCOUNT_ID=YOUR_ID
WHATSAPP_API_TOKEN=YOUR_TOKEN
WHATSAPP_VERIFY_TOKEN=clinic_queue_verify_token_2026_secure
OTP_EXPIRY_MINUTES=10
OTP_LENGTH=6
HOST=0.0.0.0
PORT=8000
```

### Step 5: Deploy

- Click **Create Web Service**
- Wait 3-5 minutes
- Get your URL: `https://clinic-queue-system.onrender.com`

✅ **Your app is LIVE!**

### Step 6: Update WhatsApp Webhook

Go back to Meta Dashboard:
- **WhatsApp → Configuration**
- **Webhook URL**: `https://clinic-queue-system.onrender.com/webhook`
- Click **Save**

Meta will verify. Green checkmark = ready! ✅

---

## 📊 API Endpoints Reference

### Health & Info
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/send-otp?phone=<phone>` | Send OTP to phone |
| GET | `/verify-otp?phone=<phone>&otp=<code>` | Verify OTP code |

### Booking
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/book?name=<name>&phone=<phone>&problem=<problem>` | Book appointment |

### Queue
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/queue-status?phone=<phone>` | Get queue position |

### Doctor
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctor/appointments` | View all bookings |

### WhatsApp
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/webhook` | Meta verification |
| POST | `/webhook` | Receive messages |
| GET | `/test-whatsapp?phone=<phone>&message=<msg>` | Test bot locally |

---

## 📁 Project Structure

```
phase-1-demo/
├── app/
│   ├── __init__.py              # Package init
│   ├── main.py                  # FastAPI app & routes
│   ├── database.py              # JSON file database
│   ├── models.py                # (Not used - kept for reference)
│   ├── schemas.py               # (Not used - kept for reference)
│   ├── otp.py                   # OTP generation & verification
│   ├── booking.py               # Queue & appointment logic
│   └── whatsapp.py              # WhatsApp chatbot
├── clinic_data.json             # Database file (auto-created)
├── requirements.txt             # Python dependencies (4 only!)
├── .env.example                 # Configuration template
└── README.md                    # This file
```

---

## 🗄️ Database

**Format**: Plain JSON file (`clinic_data.json`)

```json
{
  "patients": [
    {"id": 1, "phone": "919876543210", "name": "John", "created_at": "2026-05-06T10:00:00"}
  ],
  "appointments": [
    {"id": 1, "patient_id": 1, "token": 1, "problem": "Fever", "status": "booked", "created_at": "..."}
  ],
  "otps": [
    {"id": 1, "phone": "919876543210", "otp_code": "123456", "expires_at": "..."}
  ],
  "whatsapp_states": [
    {"id": 1, "phone": "919876543210", "state": "menu", "booking_name": "John", ...}
  ]
}
```

**No setup needed!** Just delete `clinic_data.json` to reset.

---

## 💬 WhatsApp Conversation Flow

```
User: Hi
Bot: 🏥 Welcome to Clinic Queue Management!
     What would you like to do?
     1️⃣  Book Appointment
     2️⃣  Check Queue Status

User: 1
Bot: 📝 What is your name?

User: John Doe
Bot: 🏥 What is your medical problem or complaint?

User: Fever and cough
Bot: 📋 Please confirm your booking:
     Name: John Doe
     Problem: Fever And Cough
     Reply 'YES' to confirm or 'NO' to cancel

User: YES
Bot: ✅ Appointment Booked Successfully!
     🎫 Your Token: 1
     👤 Name: John Doe
     🏥 Problem: Fever And Cough
     Please arrive on time. Your token will be called soon.
```

---

## 🔧 Troubleshooting

### ❌ "pip install" fails with build errors
**Solution**: You're using old requirements.txt with Pydantic/SQLAlchemy
```bash
# Delete venv and reinstall fresh
rmdir /s venv  # Windows
rm -rf venv    # macOS/Linux
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### ❌ "ModuleNotFoundError: No module named 'pydantic'"
**Solution**: Use the simplified requirements.txt (4 packages only)
```bash
cat requirements.txt
# Should show:
# fastapi==0.104.1
# uvicorn==0.24.0
# requests==2.31.0
# python-dotenv==1.0.0
```

### ❌ WhatsApp webhook not verified
**Solution**: 
1. Check .env VERIFY_TOKEN matches Meta Dashboard
2. Check ngrok URL is correct
3. Restart FastAPI server
4. Re-verify in Meta Dashboard

### ❌ WhatsApp messages not received
**Solution**:
1. Check your number is in test recipients
2. Check Render logs: `https://dashboard.render.com`
3. Check webhook URL is exactly correct (no typos)
4. Verify webhook (green checkmark in Meta Dashboard)

### ❌ App sleeps on Render after 15 min
**Normal on free tier!** First request wakes it up (30 sec delay).

---

## 📊 Example Responses

### Send OTP
```json
{
  "status": "success",
  "message": "OTP sent to 919876543210",
  "otp": "123456",
  "expires_in_minutes": 10
}
```

### Book Appointment
```json
{
  "status": "success",
  "token": 5,
  "message": "✓ Appointment booked! Your token: 5",
  "patient_id": 3
}
```

### Queue Status
```json
{
  "status": "success",
  "current_token": 1,
  "your_token": 5,
  "position": 5,
  "estimated_wait": "20 mins",
  "total_ahead": 4,
  "message": "You are 5th in queue"
}
```

### Doctor Dashboard
```json
{
  "status": "success",
  "count": 3,
  "appointments": [
    {
      "id": 1,
      "token": 1,
      "patient_name": "John Doe",
      "phone": "919876543210",
      "problem": "Fever",
      "status": "booked",
      "created_at": "2026-05-06T10:30:00"
    }
  ]
}
```

---

## 🎯 Share Your Live System

Once deployed on Render, share these links:

**For WhatsApp Users**:
```
Message your business number: +91 XXXXXXXXXX
They can message "Hi" to start!
```

**For Doctors**:
```
https://clinic-queue-system.onrender.com/doctor/appointments
```

**For API Users**:
```
https://clinic-queue-system.onrender.com/docs
```

---

## 🚀 What's Next?

### Phase 2 (When Ready)
Ask for "Generate Phase 2" for:
- ✅ PostgreSQL database
- ✅ Multi-clinic support
- ✅ JWT authentication
- ✅ Docker deployment
- ✅ AWS EC2 hosting
- ✅ Redis caching
- ✅ Real SMS (AWS SNS)

---

## 📚 Dependencies

Only 4 dependencies (super lightweight!):

```
fastapi==0.104.1       # Web framework
uvicorn==0.24.0        # ASGI server
requests==2.31.0       # HTTP client (for WhatsApp API)
python-dotenv==1.0.0   # Environment variables
```

**Why so few?**
- No Pydantic validation (use plain Python dicts)
- No SQLAlchemy ORM (use JSON file)
- No database drivers
- No build tools needed

**Result**: Instant installation, no errors! ✅

---

## 🎉 You're Ready!

✅ **Run locally**: 5 min
✅ **Deploy live**: 5 min
✅ **Connect WhatsApp**: 10 min
✅ **Share with team**: 1 min

**Total time to live system: ~20 minutes!**

Happy coding! 🚀🏥

---

**Made with ❤️ for clinics everywhere**
