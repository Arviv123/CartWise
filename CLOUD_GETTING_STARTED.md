# CartWise Pro Cloud - Getting Started
## מדריך התחלה למערכת הענן

---

## 🎯 מה יש לך עכשיו?

יש לך **שני מסמכים חשובים**:

1. **`CLOUD_ARCHITECTURE.md`** - תכנון ארכיטקטורה מלא
2. **`CLOUD_IMPLEMENTATION_PROMPT.md`** - פרומפט ליצירת הקוד

---

## 🚀 איך להתחיל?

### שלב 1: קרא את הארכיטקטורה

פתח את `CLOUD_ARCHITECTURE.md` וקרא אותו כדי להבין:
- את מבנה המערכת
- איך הנתונים זורמים
- מה התפקיד של כל קומפוננטה

---

### שלב 2: יצירת הקוד

יש לך **שתי אופציות**:

#### אופציה A: השתמש ב-Claude/GPT ליצירת הקוד המלא

1. פתח Claude או ChatGPT
2. פתח את `CLOUD_IMPLEMENTATION_PROMPT.md`
3. העתק את **כל** התוכן
4. הדבק ושלח
5. תקבל את כל הקוד!

**הערה**: זה פרומפט גדול מאוד. אם הבינה המלאכותית אומרת שזה יותר מדי, תוכל לפצל אותו לחלקים:
- חלק 1: Database Models
- חלק 2: API Endpoints
- חלק 3: MQTT Service
- חלק 4: Raspberry Client

---

#### אופציה B: בנה בעצמך שלב-אחר-שלב

השתמש ב-`CLOUD_IMPLEMENTATION_PROMPT.md` כמדריך ובנה כל חלק לבד.

**סדר מומלץ**:
1. Setup PostgreSQL database
2. Create database models
3. Setup FastAPI backend
4. Implement device authentication
5. Setup MQTT broker
6. Create MQTT service
7. Implement API endpoints
8. Build Raspberry Pi client
9. Test integration

---

## 📋 דרישות טכניות

### לפיתוח:

**Backend:**
- Python 3.9+
- PostgreSQL 14+
- MQTT Broker (Mosquitto)
- Redis (optional, for caching)

**Raspberry Pi:**
- Raspberry Pi 4
- Python 3.9+
- RS485 USB adapter
- Internet connection

**Frontend (Dashboard):**
- Node.js 18+
- React 18+
- TypeScript

---

### התקנות:

```bash
# PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# MQTT Broker
sudo apt-get install mosquitto mosquitto-clients

# Python dependencies (Backend)
cd cartwise-cloud/backend
pip install -r requirements.txt

# Python dependencies (Raspberry)
cd cartwise-cloud/raspberry-client
pip install -r requirements.txt

# Frontend (Dashboard)
cd cartwise-cloud/dashboard
npm install
```

---

## 🗄️ הגדרת Database

### יצירת Database

```bash
# כניסה ל-PostgreSQL
sudo -u postgres psql

# יצירת database
CREATE DATABASE cartwise_cloud;

# יצירת user
CREATE USER cartwise WITH PASSWORD 'your_password';

# הענקת הרשאות
GRANT ALL PRIVILEGES ON DATABASE cartwise_cloud TO cartwise;

# יציאה
\q
```

### Migration

```bash
# בתיקיית backend
cd cartwise-cloud/backend

# יצירת migrations
alembic revision --autogenerate -m "Initial migration"

# הרצת migrations
alembic upgrade head
```

---

## 📡 הגדרת MQTT Broker

### Mosquitto Configuration

ערוך את `/etc/mosquitto/mosquitto.conf`:

```conf
# ליסן על פורט 1883
listener 1883

# אפשר anonymous (לפיתוח בלבד!)
allow_anonymous true

# בייצור, הגדר אימות:
# password_file /etc/mosquitto/passwd
```

הפעל מחדש:
```bash
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```

### יצירת משתמש MQTT (ייצור)

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd cartwise
# הזן סיסמה

# עדכן mosquitto.conf:
# allow_anonymous false
# password_file /etc/mosquitto/passwd

sudo systemctl restart mosquitto
```

---

## 🔧 הגדרת Environment Variables

### Backend (`.env`)

```bash
cd cartwise-cloud/backend
cp .env.example .env
```

ערוך `.env`:
```env
# Database
DATABASE_URL=postgresql://cartwise:your_password@localhost/cartwise_cloud

# API
API_HOST=0.0.0.0
API_PORT=8000

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=cartwise
MQTT_PASSWORD=your_mqtt_password

# Security
SECRET_KEY=your-super-secret-key-here-generate-with-openssl

# SMS (Inforu)
INFORU_USERNAME=your_inforu_username
INFORU_PASSWORD=your_inforu_password
```

### Raspberry Client (`config.json`)

```bash
cd cartwise-cloud/raspberry-client
cp config.example.json config.json
```

ערוך `config.json`:
```json
{
  "device_name": "RPi-Branch-001",
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "serial_number": "RPI-12345",
  "branch_code": "BRANCH-001",
  "cloud_api_url": "https://your-cloud-api.com/api",
  "mqtt": {
    "broker": "your-cloud-api.com",
    "port": 8883,
    "use_tls": true,
    "username": "cartwise",
    "password": "your_mqtt_password"
  },
  "rs485": {
    "port": "/dev/ttyUSB0",
    "baudrate": 19200
  }
}
```

---

## 🚀 הפעלת המערכת

### 1. הפעל Backend

```bash
cd cartwise-cloud/backend
python main.py
```

או עם uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. בדוק API

פתח דפדפן:
```
http://localhost:8000/docs
```

תראה Swagger UI עם כל ה-endpoints!

### 3. הפעל Raspberry Client (בטסט מקומי)

```bash
cd cartwise-cloud/raspberry-client
python main.py
```

תראה:
```
Starting CartWise Raspberry Pi Client
Registering device with cloud...
Device registered: <uuid>
Connecting to MQTT broker...
Initializing RS485 controller...
```

---

## 📊 יצירת נתוני טסט

### דרך API (Swagger UI)

1. גש ל-`http://localhost:8000/docs`
2. צור Chain:
   ```json
   {
     "name": "רמי לוי",
     "slug": "rami-levi"
   }
   ```
3. צור Branch:
   ```json
   {
     "chain_id": "<chain_uuid>",
     "name": "סניף ירושלים",
     "branch_code": "BRANCH-001",
     "city": "ירושלים"
   }
   ```
4. רשום Device (יקרה אוטומטית כשה-Raspberry יתחבר)

### דרך Python Script

```python
import requests

API_URL = "http://localhost:8000/api"

# Create chain
chain_data = {
    "name": "רמי לוי",
    "slug": "rami-levi"
}
response = requests.post(f"{API_URL}/chains", json=chain_data)
chain = response.json()

# Create branch
branch_data = {
    "chain_id": chain["id"],
    "name": "סניף ירושלים",
    "branch_code": "BRANCH-001",
    "city": "ירושלים"
}
response = requests.post(f"{API_URL}/branches", json=branch_data)
branch = response.json()

print(f"Created chain: {chain['id']}")
print(f"Created branch: {branch['id']}")
```

---

## 🧪 בדיקת MQTT

### בדיקה עם Mosquitto Client

**Terminal 1 (Subscribe)**:
```bash
mosquitto_sub -h localhost -t "cartwise/#" -v
```

**Terminal 2 (Publish)**:
```bash
mosquitto_pub -h localhost -t "cartwise/rami-levi/BRANCH-001/devices/test/status" -m '{"status":"online"}'
```

תראה בTerminal 1:
```
cartwise/rami-levi/BRANCH-001/devices/test/status {"status":"online"}
```

---

## 📱 Dashboard

אם יצרת Dashboard (React), הפעל אותו:

```bash
cd cartwise-cloud/dashboard
npm run dev
```

פתח דפדפן:
```
http://localhost:5173
```

---

## 🐛 פתרון בעיות

### Backend לא עולה

**שגיאה**: `ConnectionRefusedError: [Errno 111] Connection refused`

**פתרון**: בדוק ש-PostgreSQL רץ:
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

---

### MQTT לא מתחבר

**שגיאה**: `Connection refused`

**פתרון**: בדוק ש-Mosquitto רץ:
```bash
sudo systemctl status mosquitto
sudo systemctl start mosquitto
```

בדוק שהפורט פתוח:
```bash
netstat -tuln | grep 1883
```

---

### Raspberry לא מצליח לרשום

**שגיאה**: `Failed to register device: Connection refused`

**פתרון**:
1. בדוק שה-Backend רץ
2. בדוק שכתובת ה-API ב-`config.json` נכונה
3. בדוק חיבור אינטרנט

---

### Database Migration נכשל

**שגיאה**: `sqlalchemy.exc.OperationalError`

**פתרון**:
1. בדוק ש-DATABASE_URL נכון ב-`.env`
2. בדוק שיש לך הרשאות ל-database
3. בדוק ש-PostgreSQL רץ

---

## 📖 קריאה נוספת

### ארכיטקטורה ותכנון:
- [`CLOUD_ARCHITECTURE.md`](CLOUD_ARCHITECTURE.md)

### יצירת הקוד:
- [`CLOUD_IMPLEMENTATION_PROMPT.md`](CLOUD_IMPLEMENTATION_PROMPT.md)

### מערכת הקיימת:
- [`README.md`](README.md)
- [`START_HERE.md`](START_HERE.md)
- [`docs/api/`](docs/api/)

---

## 🎯 Next Steps

לאחר שהכל עובד מקומית:

1. **Deploy Backend ל-Cloud**
   - AWS / Azure / Google Cloud
   - Render.com (כמו המערכת הקיימת)
   - Heroku

2. **Setup Production MQTT**
   - AWS IoT Core
   - CloudMQTT
   - HiveMQ Cloud

3. **Deploy Dashboard**
   - Vercel
   - Netlify
   - AWS S3 + CloudFront

4. **Install על Raspberry Pi**
   - העתק את `raspberry-client/`
   - הגדר `config.json`
   - הפעל כ-systemd service

---

## 💡 טיפים חשובים

### Development vs Production

**Development**:
- SQLite לטסטים מהירים
- MQTT ללא TLS
- Debug mode מופעל

**Production**:
- PostgreSQL עם backups
- MQTT עם TLS
- HTTPS בלבד
- Rate limiting
- Monitoring

### Security

1. **לעולם אל**:
   - תשתמש ב-`allow_anonymous` בייצור
   - תשלח סיסמאות ב-plain text
   - תשמור `.env` ב-Git

2. **תמיד**:
   - השתמש ב-HTTPS/TLS
   - Generate strong SECRET_KEY
   - הגדר CORS נכון
   - השתמש ב-environment variables

---

## ✅ Checklist לפני ייצור

- [ ] PostgreSQL מוגדר עם backups
- [ ] MQTT עם TLS ואימות
- [ ] Backend עם HTTPS
- [ ] Environment variables מוגדרים
- [ ] Database migrations עברו
- [ ] Tests עוברים
- [ ] Logging מופעל
- [ ] Monitoring מוגדר (Prometheus/Grafana)
- [ ] Error tracking (Sentry)
- [ ] Documentation מעודכן

---

**Version:** 2.0.0
**Last Updated:** 2025-10-24
**Status:** Ready for Implementation!

**🎉 בהצלחה!**
