# מדריך התחלה מהירה - CartWise Pro (גרסה מרופקטרת)

## מבנה הפרויקט החדש

```
CartWise-Pro/
├── src/                          # קוד מקור ראשי
│   ├── main.py                  # נקודת כניסה למערכת
│   ├── core/                    # ליבת המערכת
│   │   ├── config.py           # קונפיגורציה מרכזית
│   │   ├── logging.py          # מערכת לוגים משודרגת
│   │   └── constants.py        # קבועים גלובליים
│   ├── api/                     # API endpoints
│   │   ├── app.py              # FastAPI setup
│   │   ├── dependencies.py     # Dependency injection
│   │   └── routers/            # Endpoints מפוצלים
│   │       ├── auth.py         # אימות OTP
│   │       ├── carts.py        # ניהול עגלות
│   │       └── health.py       # בריאות המערכת
│   ├── models/                  # מבני נתונים
│   ├── providers/               # ספקי שירות חיצוניים
│   │   └── sms/                # SMS providers
│   ├── hardware/                # אינטגרציות חומרה
│   │   └── rs485.py            # RS485 controller
│   └── utils/                   # פונקציות עזר
│       ├── validation.py       # ואלידציה
│       ├── otp.py              # ניהול OTP
│       └── messaging.py        # הודעות
├── config/                      # קבצי הגדרות
│   └── .env                    # משתני סביבה
├── logs/                        # קבצי לוג (נוצר אוטומטית)
│   └── cartwise.log            # לוג ראשי
├── public/                      # קבצים סטטיים
│   └── index.html              # ממשק לקוח
├── REFACTORING_SUMMARY.md       # סיכום מפורט של השינויים
└── requirements.txt             # תלויות Python
```

---

## התקנה והרצה

### 1. התקנת תלויות

```bash
pip install -r requirements.txt
```

### 2. הגדרת משתני סביבה

ערוך את הקובץ `config/.env`:

```env
# SMS Configuration (Inforu)
INFORU_USERNAME=your_username_here
INFORU_PASSWORD=your_password_here

# RS485 Serial Port
SERIAL_PORT=/dev/ttyUSB0
BAUD_RATE=9600

# Server Configuration
HOST=0.0.0.0
PORT=8001

# OTP Configuration
OTP_LENGTH=4
OTP_EXPIRATION_MINUTES=5

# Logging
LOG_LEVEL=INFO
```

### 3. הרצת השרת

```bash
cd src
python main.py
```

השרת יעלה על: `http://localhost:8001`

---

## מערכת הלוגים החדשה

### תכונות:

✅ **כתיבה דו-כיוונית:**
- **קונסול/טרמינל** - output צבעוני בזמן אמת
- **קובץ** - `logs/cartwise.log` עם rotation אוטומטי

✅ **צבעים:**
- 🔵 DEBUG - ציאן
- 🟢 INFO - ירוק
- 🟡 WARNING - צהוב
- 🔴 ERROR - אדום
- 🟣 CRITICAL - סגול

### בדיקת מערכת הלוגים:

```bash
cd src
python logging_demo.py
```

פלט צפוי:
- **טרמינל:** לוגים צבעוניים בזמן אמת
- **קובץ:** `logs/cartwise.log` עם כל הלוגים

---

## API Endpoints

### בריאות המערכת

```bash
GET  /health              # בדיקת בריאות
GET  /stats               # סטטיסטיקות
```

### אימות

```bash
POST /auth/request-otp    # בקשת קוד OTP
POST /auth/verify-otp     # אימות OTP
```

### עגלות

```bash
GET  /carts               # כל העגלות
GET  /carts/available     # עגלות זמינות
GET  /carts/{id}          # עגלה ספציפית
POST /carts/assign        # הקצאת עגלה
POST /carts/{id}/return   # החזרת עגלה
```

### תיעוד API אינטראקטיבי:

פתח בדפדפן: `http://localhost:8001/docs`

---

## שימוש בלוגים בקוד שלך

```python
from core import setup_logging, get_logger

# הגדר פעם אחת בתחילת האפליקציה
setup_logging()

# קבל logger בכל מודול
logger = get_logger(__name__)

# השתמש בו
logger.info("Operation started")
logger.debug("Variable value: %s", my_var)
logger.warning("Unusual condition")
logger.error("Operation failed", exc_info=True)
```

---

## שינויים עיקריים מהגרסה הקודמת

### 1. מבנה מודולרי
- `main.py` - רק 40 שורות (במקום 493!)
- קוד מפוצל ל-routers נפרדים

### 2. אין קוד חוזר (DRY)
- קונפיגורציה מרכזית ב-`core/config.py`
- קבועים ב-`core/constants.py`
- פונקציות עזר ב-`utils/`

### 3. מערכת לוגים משודרגת
- כתיבה לקובץ + טרמינל
- צבעים
- Rotation אוטומטי

### 4. Dependency Injection
- ניהול מופעים מרכזי
- קל לבדיקות

---

## בדיקת תקינות

### בדיקת syntax:

```bash
cd src
python -m py_compile main.py
```

### (אופציונלי) הרצת בדיקות איכות:

```bash
flake8 src/
black src/ --check
```

---

## טיפים

### צפייה בלוגים בזמן אמת:

**Linux/Mac:**
```bash
tail -f logs/cartwise.log
```

**Windows:**
```powershell
Get-Content logs\cartwise.log -Wait -Tail 50
```

### שינוי רמת לוגים:

ערוך `config/.env`:
```env
LOG_LEVEL=DEBUG  # או INFO, WARNING, ERROR
```

---

## קריאה נוספת

- **סיכום מפורט של הרפקטורינג:** `REFACTORING_SUMMARY.md`
- **דוגמה למערכת לוגים:** `src/logging_demo.py`
- **תיעוד מקורי:** `README.md`
- **מדריך deployment:** `DEPLOYMENT_CHECKLIST.md`

---

## תמיכה

בעיות? ראה:
1. `logs/cartwise.log` - לוגים מפורטים
2. `http://localhost:8001/health` - בריאות המערכת
3. `REFACTORING_SUMMARY.md` - מדריך מפורט

---

**גרסה:** 1.0.0 (Refactored)
**עדכון אחרון:** 2025-10-21
**צוות:** CartWise Team
