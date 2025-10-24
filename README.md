# CartWise Pro - Smart Shopping Cart Management System
### מערכת ניהול עגלות קניות חכמות

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00d485.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**🚀 Live Demo**: [https://cartwise-api.onrender.com](https://cartwise-api.onrender.com) (זמין בקרוב)

---

## 📋 תוכן עניינים

- [סקירה כללית](#סקירה-כללית)
- [תכונות עיקריות](#תכונות-עיקריות)
- [ארכיטקטורה](#ארכיטקטורה)
- [התקנה מהירה](#התקנה-מהירה)
- [פריסה לייצור](#פריסה-לייצור)
- [תיעוד API](#תיעוד-api)
- [Dashboard](#dashboard)
- [פיתוח](#פיתוח)

---

## 🎯 סקירה כללית

**CartWise Pro** היא מערכת מתקדמת לניהול עגלות קניות חכמות, בדומה למערכת של רמי לוי.
המערכת מאפשרת ללקוחות להשתמש בעגלות באמצעות אימות SMS ושליטה אלקטרונית במנעולים.

### מטרות הפרויקט

1. **חווית משתמש מעולה** - ממשק פשוט ונוח לשימוש
2. **אבטחה מלאה** - אימות דו-שלבי עם SMS
3. **אמינות גבוהה** - מערכת יציבה עם טיפול בשגיאות
4. **קלות תחזוקה** - קוד נקי, מתועד ומבנה ברור
5. **הרחבה עתידית** - ארכיטקטורה מודולרית

---

## ✨ תכונות עיקריות

### 1. ניהול לקוחות
- ✅ אימות משתמש באמצעות מספר טלפון
- ✅ שליחת קוד OTP דרך SMS (Inforu API v2)
- ✅ וידוא קוד והקצאת עגלה

### 2. שליטה במנעולים
- ✅ חיבור RS485 לבקר מנעולים
- ✅ פתיחה ונעילה של מנעולים בפרוטוקול ייעודי
- ✅ זיהוי החזרת עגלה (Micro-Switch)
- ✅ CRC Checksum לאימות תקשורת

### 3. ממשק משתמש
- ✅ עיצוב מודרני ונקי (בסגנון רמי לוי)
- ✅ תמיכה במסכי מגע
- ✅ תמיכה בעברית ובאנגלית
- ✅ נגישות WCAG 2.1

### 4. מערכת מעקב השכרות
- ✅ מעקב אחר כל השכרה (Rental Tracking)
- ✅ זיהוי אוטומטי של איחורים
- ✅ שליחת SMS תזכורת אוטומטית
- ✅ היסטוריה מלאה של השכרות
- ✅ סטטיסטיקות ודוחות

### 5. אימות מתקדם
- ✅ מערכת אימות חד-פעמית (OTP)
- ✅ טוקן אימות ל-30 יום
- ✅ משתמשים חוזרים ללא צורך ב-OTP
- ✅ אבטחה מלאה

### 6. API ושרת
- ✅ FastAPI - מהיר, מודרני ומתועד אוטומטית
- ✅ REST API עם Swagger documentation
- ✅ תמיכה ב-Docker
- ✅ ניתן לפריסה ב-Render/Heroku/AWS
- ✅ Logging מפורט

---

## 🏗️ ארכיטקטורה

```
CartWise-Pro/
├── src/
│   ├── api/              # FastAPI backend
│   │   ├── main.py       # Application entry point
│   │   ├── routes.py     # API endpoints
│   │   └── middleware.py # Middleware & error handling
│   ├── hardware/         # Hardware communication
│   │   ├── rs485.py      # RS485 controller
│   │   └── protocol.py   # Communication protocol
│   ├── sms/              # SMS integration
│   │   ├── inforu.py     # Inforu SMS provider
│   │   └── otp.py        # OTP generation & validation
│   └── models/           # Data models
│       ├── cart.py       # Cart model
│       └── user.py       # User model
├── public/               # Frontend
│   ├── index.html        # Customer interface
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript
├── docs/                 # Documentation
│   ├── API.md            # API documentation
│   ├── HARDWARE.md       # Hardware setup
│   └── DEPLOYMENT.md     # Deployment guide
├── tests/                # Unit & integration tests
├── config/               # Configuration files
│   ├── .env.example      # Environment variables template
│   └── settings.py       # App settings
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── setup.py              # Installation script
```

---

## 🚀 התקנה מהירה

### דרישות מערכת

- **Python**: 3.8 ואילך
- **מערכת הפעלה**: Linux / Windows / macOS
- **חומרה (אופציונלי)**:
  - Raspberry Pi 4 (לשימוש עם מנעולים)
  - USB-RS485 Adapter
  - בקר מנעולים KERONG CU16

### התקנה - Development

```bash
# 1. Clone the repository
git clone https://github.com/Arviv123/CartWise.git
cd CartWise

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# ערוך את .env עם הפרטים שלך

# 4. Run the application
python run_server.py
```

**הדפדפן יפתח אוטומטית**: `http://localhost:8002`

### הגדרות סביבה (`.env`)

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8002

# SMS Provider (Inforu)
INFORU_USERNAME=your_username
INFORU_PASSWORD=your_password

# Demo Mode (set to 'true' to run without hardware)
DEMO_MODE=true

# RS485 Serial Port (only needed when DEMO_MODE=false)
RS485_PORT=COM3
RS485_BAUDRATE=19200

# OTP Configuration
OTP_EXPIRATION_MINUTES=5

# Cart Rental Duration (in hours)
RENTAL_DURATION_HOURS=2
```

---

## 🌐 פריסה לייצור

### Option 1: Render.com (מומלץ)

1. **צור חשבון ב-[Render.com](https://render.com)**

2. **צור Web Service חדש**:
   - Source Code: `https://github.com/Arviv123/CartWise`
   - Environment: **Docker**
   - Branch: `main`
   - Instance Type: **Free** (לפיתוח) או **Starter** (לייצור)

3. **הוסף Environment Variables**:
   ```
   DEMO_MODE=true
   INFORU_USERNAME=your_username
   INFORU_PASSWORD=your_password
   ```

4. **Deploy!**

**📖 מדריך מפורט**: ראה [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

### Option 2: Docker

```bash
# Build
docker build -t cartwise-pro .

# Run
docker run -d -p 8002:8002 \
  -e DEMO_MODE=true \
  -e INFORU_USERNAME=your_username \
  -e INFORU_PASSWORD=your_password \
  cartwise-pro
```

### Option 3: Manual Deployment

```bash
# על שרת Linux
git clone https://github.com/Arviv123/CartWise.git
cd CartWise
pip install -r requirements.txt
python run_server.py
```

---

## 📱 שימוש

### הפעלת השרת

```bash
python run_server.py
```

השרת יעלה על: `http://localhost:8002`

הדפדפן יפתח אוטומטית עם הממשק ללקוח.

### גישה לממשק משתמש

```
http://localhost:8002/
```

### API Documentation

Swagger UI (תיעוד אינטראקטיבי) זמין ב:
```
http://localhost:8002/docs
```

### תיעוד מלא

תיעוד API מקיף זמין בתיקייה:
```
docs/api/
```

או בקובץ HTML:
```
docs/api/API_Documentation.html
```

---

## 📊 Dashboard

רוצה ליצור Dashboard ניהול?

**📝 הפרומפט המלא**: [DASHBOARD_PROMPT.md](DASHBOARD_PROMPT.md)

הפרומפט כולל:
- מבנה פרויקט מלא
- כל ה-API endpoints
- דוגמאות קוד
- הוראות עיצוב
- טיפים לפיתוח

העתק את הפרומפט ל-Claude/ChatGPT ותקבל Dashboard מלא!

---

## 📚 תיעוד API

### Endpoints עיקריים

#### Authentication
- `POST /auth/request-otp` - שליחת קוד OTP
- `POST /auth/verify-otp` - אימות קוד והנפקת טוקן

#### Carts
- `GET /carts` - קבלת רשימת עגלות
- `POST /carts/assign` - הקצאת עגלה למשתמש
- `POST /carts/initiate-return` - התחלת החזרה
- `POST /carts/complete-return` - סיום החזרה

#### Rentals
- `GET /rentals/active` - השכרות פעילות
- `GET /rentals/overdue` - השכרות באיחור
- `GET /rentals/history` - היסטוריית השכרות
- `GET /rentals/stats/summary` - סטטיסטיקות

**📖 תיעוד מפורט**:
- Swagger UI: `http://localhost:8002/docs`
- קבצי תיעוד: `docs/api/`
- HTML: `docs/api/API_Documentation.html`

### Hardware Integration

#### פרוטוקול KERONG CU16
- **Baud Rate**: 19200
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Frame Format**: STX + ADDR + CMD + ETX + SUM

#### Demo Mode
המערכת תומכת ב-Demo Mode לפיתוח ללא חומרה:
```env
DEMO_MODE=true
```

בעת פעולה ללא חומרה:
- כל הפעולות מתבצעות בהצלחה
- אין צורך ב-RS485 adapter
- מושלם לפיתוח ובדיקות

---

## 🛠️ פיתוח

### הרצת Tests

```bash
pytest tests/
```

### Code Style

הפרויקט משתמש ב:
- **Black** - Code formatter
- **Flake8** - Linter
- **MyPy** - Type checker

```bash
black src/
flake8 src/
mypy src/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📁 מסמכים חשובים

### המערכת הקיימת (Single Branch):

| מסמך | תיאור |
|------|--------|
| [START_HERE.md](START_HERE.md) | 🚀 **התחל כאן!** - מדריך התחלה מהיר |
| [RENDER_SETUP_ANSWERS.md](RENDER_SETUP_ANSWERS.md) | תשובות מדויקות לטופס Render.com |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | מדריך פריסה מלא שלב-אחר-שלב |
| [DASHBOARD_PROMPT.md](DASHBOARD_PROMPT.md) | פרומפט ליצירת Dashboard ניהול |
| [docs/api/](docs/api/) | תיעוד API מקיף |

### מערכת ענן רב-סניפית (Multi-Tenant Cloud):

| מסמך | תיאור |
|------|--------|
| [CLOUD_ARCHITECTURE.md](CLOUD_ARCHITECTURE.md) | 🏗️ **ארכיטקטורת הענן** - תכנון מלא למערכת רב-סניפית |
| [CLOUD_IMPLEMENTATION_PROMPT.md](CLOUD_IMPLEMENTATION_PROMPT.md) | 📝 **פרומפט יצירה** - העבר ל-AI ליצירת כל הקוד |
| [CLOUD_GETTING_STARTED.md](CLOUD_GETTING_STARTED.md) | 🚀 **מדריך התחלה** - איך להתחיל עם מערכת הענן |

---

## 📞 תמיכה

לשאלות ותמיכה:
- **GitHub Issues**: [CartWise Issues](https://github.com/Arviv123/CartWise/issues)
- **Email**: support@cartwise.com

---

## 📄 רישיון

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 תודות

- **Inforu** - SMS API Provider
- **FastAPI** - Modern web framework
- **Community** - Open source contributors

---

**Created with ❤️ by the CartWise Team**
