# 🏥 Clinic Queue Management System - PHASE 1 DEMO

A fully working, **completely FREE** clinic appointment and queue management system with WhatsApp integration. Deploy in minutes, use immediately.

---

## ⚡ What You Get

### ✅ Working Features
- **OTP Authentication**: SMS-like OTP verification (printed to console in demo)
- **Appointment Booking**: Patients can book with name, phone, and problem
- **Real-time Queue**: See current token, your position, and wait time
- **WhatsApp Chatbot**: Guided booking and status check via WhatsApp
- **Doctor Dashboard**: View all bookings and appointments
- **SQLite Database**: File-based, no setup needed

### ✅ Ready to Deploy
- **Render (Free)**: Deploy for $0/month with auto HTTPS
- **Docker Ready**: Phase 2 includes Docker support
- **API Documentation**: Interactive Swagger UI at `/docs`

### ✅ Production Ready
- Type hints and validation throughout
- Error handling and logging
- Environment-based configuration
- Modular, testable code

---

## 🚀 Quick Start (3 Minutes)

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

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure (Optional)
```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (mostly pre-configured for demo)
# cat .env
```

### Step 5: Run!
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Server running at**: `http://localhost:8000`

---

## 🧪 Test It Now

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Send OTP
```bash
curl -X POST http://localhost:8000/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "919876543210"}'
```
Check console for OTP! It will print something like: `📱 OTP for 919876543210: 123456`

### 3. Verify OTP
```bash
curl -X POST http://localhost:8000/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "919876543210", "otp": "123456"}'
```

### 4. Book Appointment
```bash
curl -X POST http://localhost:8000/book \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "919876543210",
    "problem": "Fever and cough"
  }'
```
Response: `{"status": "success", "token": 1, "message": "✓ Appointment booked! Your token: 1"}`

### 5. Check Queue Status
```bash
curl http://localhost:8000/queue-status?phone=919876543210
```
Response:
```json
{
  "status": "success",
  "current_token": 1,
  "your_token": 1,
  "position": 1,
  "estimated_wait": "Your turn!",
  "total_ahead": 0,
  "message": "You are 1st in queue"
}
```

### 6. Doctor Dashboard
```bash
curl http://localhost:8000/doctor/appointments
```

### 7. Interactive API Docs
Visit: `http://localhost:8000/docs`

Everything is documented with request/response examples. You can "Try It Out" directly in browser!

---

## 📱 WhatsApp Integration (Test Mode)

### Option A: Use ngrok (Test Locally Without Deployment)

1. **Download ngrok**: https://ngrok.com/download
2. **Start ngrok** (in another terminal):
   ```bash
   ngrok http 8000
   ```
   You'll get a URL like: `https://xxxxx-xx-xxx.ngrok.io`

3. **Setup WhatsApp Webhook**:
   - Go to https://developers.facebook.com/apps
   - Select your App
   - Go to **WhatsApp** → **Configuration**
   - Set **Webhook URL**: `https://xxxxx-xx-xxx.ngrok.io/webhook`
   - Set **Verify Token**: `demo_verify_token` (or change in .env)
   - Click **Verify and Save**

4. **Test with WhatsApp Business Account**:
   - Add your phone number to test recipients
   - Send message to the business number: "Hi"
   - Bot responds with menu

### Option B: Deploy to Render First (Recommended)

See deployment section below.

---

## 🌐 Deploy to Render (FREE Tier) - 5 Minutes

### Prerequisites
- GitHub account (code already pushed)
- Render account (free at render.com)

### Step-by-Step

#### 1. Create Render Account & Connect GitHub
- Go to https://render.com
- Sign up with GitHub
- Connect your GitHub account

#### 2. Create New Web Service
- Click **New +** → **Web Service**
- Search for `clinic-queue-system`
- Select the repository
- Click **Connect**

#### 3. Configure Deployment
Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | clinic-queue-system |
| **Environment** | Python 3 |
| **Region** | Choose closest to you |
| **Build Command** | `pip install -r phase-1-demo/requirements.txt` |
| **Start Command** | `cd phase-1-demo && uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| **Instance Type** | Free |

#### 4. Add Environment Variables
Click **Environment** in left sidebar:

```
FASTAPI_ENV=production
DATABASE_URL=sqlite:///./clinic.db
WHATSAPP_PHONE_NUMBER_ID=your_id (optional for demo)
WHATSAPP_API_TOKEN=your_token (optional for demo)
WHATSAPP_VERIFY_TOKEN=demo_verify_token
```

#### 5. Deploy
- Click **Create Web Service**
- Wait 2-3 minutes
- ✅ You'll get a URL like: `https://clinic-queue-system.onrender.com`

#### 6. Verify Deployment
```bash
curl https://clinic-queue-system.onrender.com/health
```

#### 7. Connect WhatsApp (Optional)
- Go to Meta Developer Dashboard
- WhatsApp Configuration
- Set Webhook URL: `https://clinic-queue-system.onrender.com/webhook`
- Set Verify Token: `demo_verify_token`
- Save

---

## 📊 API Endpoints Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/send-otp` | Send OTP to phone |
| POST | `/verify-otp` | Verify OTP code |

### Booking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/book` | Book appointment |

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

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI docs |
| GET | `/redoc` | ReDoc documentation |

---

## 📁 Project Structure

```
phase-1-demo/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI app and routes
│   ├── database.py              # SQLite setup and session
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic validation schemas
│   ├── otp.py                   # OTP generation and verification
│   ├── booking.py               # Appointment and queue logic
│   └── whatsapp.py              # WhatsApp chatbot and webhook
├── clinic.db                    # SQLite database (auto-created)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## 🗄️ Database Schema

### patients
```sql
id (PK)         -- Auto-increment ID
phone (UNIQUE)  -- Phone number (unique per patient)
name            -- Patient name
created_at      -- Registration timestamp
```

### appointments
```sql
id (PK)         -- Auto-increment ID
patient_id (FK) -- Reference to patient
token (UNIQUE)  -- Queue token number
problem         -- Medical problem/complaint
status          -- booked | completed | no_show | cancelled
created_at      -- Booking timestamp
updated_at      -- Last update timestamp
```

### otps
```sql
id (PK)         -- Auto-increment ID
phone           -- Phone number OTP was sent to
otp_code        -- 6-digit OTP
created_at      -- When OTP was generated
expires_at      -- Expiry time (10 mins)
patient_id (FK) -- Optional reference to patient
```

### whatsapp_states
```sql
id (PK)         -- Auto-increment ID
phone (UNIQUE)  -- Phone number unique
patient_id (FK) -- Reference to patient
state           -- Conversation state
booking_name    -- Name during booking flow
booking_problem -- Problem during booking flow
created_at      -- When conversation started
updated_at      -- Last update
```

---

## 🔐 Security Notes

### ✅ Demo Phase (Phase 1)
- OTP printed to console for testing
- No JWT authentication required
- SQLite database (single-user friendly)
- HTTPS via Render (auto-enabled)

### 🔒 Phase 2 (Production)
- JWT-based authentication
- AWS SNS for real SMS
- PostgreSQL for scalability
- Rate limiting
- Input validation & sanitization

---

## 🛠️ Development Tips

### Run with Auto-Reload
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### View API Documentation
- **Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Check Database
```bash
# SQLite interactive mode
sqlite3 clinic.db

# View tables
.tables

# View patients
SELECT * FROM patients;

# Exit
.quit
```

### Debug WhatsApp Messages
All WhatsApp messages are logged to console. Look for:
```
📱 Message from 919876543210: Hi
✓ Responded: Welcome to Clinic Queue!...
```

---

## 🐛 Troubleshooting

### "Address already in use" Error
Another app is using port 8000. Change port:
```bash
python -m uvicorn app.main:app --port 8001
```

### OTP Not Showing
Check console output where you ran the app. Search for:
```
📱 OTP for 919876543210: 123456
```

### WhatsApp Not Responding
1. Check webhook is verified (green checkmark in Meta Dashboard)
2. Check Verify Token matches in .env
3. Check logs in console for errors
4. In test mode, only registered numbers can receive messages

### Database Lock Error
Close any other connections to clinic.db and restart:
```bash
rm clinic.db  # Delete old database
python -m uvicorn app.main:app --reload
```

---

## 📈 Example Responses

### Successful OTP Send
```json
{
  "status": "success",
  "message": "OTP sent to your phone",
  "otp": "123456"
}
```

### Successful Booking
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

## 🚢 What's Next?

### Phase 2 Features (Coming Soon)
- ✅ Multi-clinic support
- ✅ Multi-doctor with separate queues
- ✅ PostgreSQL database
- ✅ JWT authentication
- ✅ AWS SNS real SMS
- ✅ Redis caching
- ✅ Docker deployment
- ✅ EC2/AWS hosting guide

---

## 📚 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **SQLAlchemy**: https://docs.sqlalchemy.org
- **Pydantic**: https://docs.pydantic.dev
- **WhatsApp Cloud API**: https://developers.facebook.com/docs/whatsapp/cloud-api
- **Render Deployment**: https://render.com/docs

---

## 📞 Support

### Common Issues?
Check the Troubleshooting section above.

### Want to Contribute?
This is Phase 1. Phase 2 improvements welcome!

### Found a Bug?
Create an issue on GitHub with:
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

---

## 📄 License

This project is open source. Feel free to use, modify, and deploy!

---

## 🎉 You're Ready!

**Your clinic queue system is ready to go live!**

Choose your next step:
1. **Test locally** → Follow "Quick Start" above
2. **Deploy to Render** → Follow "Deploy to Render" above
3. **Connect WhatsApp** → Follow "WhatsApp Integration" above
4. **See Phase 2** → Ask for "Phase 2 Production System"

Happy coding! 🚀

---

**Made with ❤️ for clinics everywhere** 🏥
