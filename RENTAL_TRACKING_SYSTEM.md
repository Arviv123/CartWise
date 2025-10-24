# 📊 מערכת מעקב השכרות - Rental Tracking System

## סקירה כללית

מערכת מעקב מלאה אחרי השכרות עגלות כולל:
- ✅ שמירת כל ההיסטוריה ב-SQLite
- ✅ זיהוי אוטומטי של החזרות דרך בקר CU16
- ✅ מעקב אחרי איחורים וזמנים
- ✅ תהליך רקע שבודק כל 5 שניות
- ✅ זמן ברירת מחדל להחזרה: 120 דקות (שעתיים)

---

## 🏗️ ארכיטקטורה

### רכיבים חדשים

```
src/
├── models/
│   └── rental.py              # מודל Rental עם סטטוסים
├── utils/
│   └── database.py            # RentalDatabase (SQLite)
├── hardware/
│   └── cu16_monitor.py        # CU16Monitor - תהליך רקע
└── api/
    └── routers/
        └── rentals.py         # API endpoints להיסטוריה
```

### מסד נתונים

**קובץ:** `data/rentals.db` (SQLite)

**טבלה:** `rentals`
```sql
CREATE TABLE rentals (
    rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    user_phone TEXT NOT NULL,
    locker_id INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    expected_return TEXT NOT NULL,
    actual_return TEXT,
    status TEXT NOT NULL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

**אינדקסים:**
- `idx_user_phone` - חיפוש מהיר לפי טלפון
- `idx_status` - סינון לפי סטטוס
- `idx_cart_id` - חיפוש לפי עגלה

---

## 📋 מודל Rental

### סטטוסים

| Status | תיאור | מתי קורה |
|--------|-------|----------|
| `active` | השכרה פעילה | כשלוקחים עגלה |
| `returned` | הוחזרה בזמן | הוחזרה לפני `expected_return` |
| `returned_late` | הוחזרה באיחור | הוחזרה אחרי `expected_return` |
| `overdue` | לא הוחזרה | עברו `expected_return` ועדיין בשימוש |
| `cancelled` | בוטלה | בוטל ידנית |

### מאפיינים

```python
class Rental:
    rental_id: int               # מזהה ייחודי
    cart_id: int                 # מספר עגלה
    user_phone: str              # טלפון משתמש
    locker_id: int               # מספר מנעול פיזי

    start_time: datetime         # זמן התחלה
    expected_return: datetime    # זמן מתוכנן להחזרה
    actual_return: datetime      # זמן החזרה בפועל (None אם עדיין בשימוש)

    status: RentalStatus         # סטטוס נוכחי
    notes: str                   # הערות

    # Properties
    @property
    def is_late(self) -> bool           # האם באיחור?
    def time_remaining(self) -> timedelta  # זמן שנותר
    def duration(self) -> timedelta        # משך השכרה
```

---

## 🤖 CU16 Monitor Service

### תפקיד

תהליך רקע שרץ כל 5 שניות ובודק:
1. **זיהוי החזרות אוטומטי** - קורא את מצב כל המנעולים מהבקר
2. **איתור איחורים** - מסמן השכרות שעברו את הזמן כ-`overdue`
3. **עדכון מסד נתונים** - מעדכן סטטוסים אוטומטית

### איך זה עובד?

```python
# כל 5 שניות:
1. שאילתה לבקר CU16 → קבלת מצב כל 16 המנעולים
2. לכל השכרה פעילה:
   - בדוק: האם יש עגלה במנעול (infrared)
   - בדוק: האם המנעול נעול (lock hook)
   - אם שניהם = TRUE → העגלה הוחזרה!
3. עדכן rental ב-DB:
   - actual_return = NOW
   - status = returned או returned_late
4. עדכן את ה-Cart:
   - status = available
   - assigned_to = None
```

### קוד לדוגמה

```python
from hardware.cu16_monitor import CU16MonitorSync

# אתחול
monitor = CU16MonitorSync(
    lock_controller=rs485_controller,
    rental_db=rental_db,
    carts_db=carts_db,
    check_interval=5  # בדוק כל 5 שניות
)

# התחלה
monitor.start()

# עצירה
monitor.stop()
```

---

## 🔌 API Endpoints

### 1. השכרת עגלה (עם יצירת rental)

```http
POST /carts/assign
Content-Type: application/json

{
  "phone": "0501234567",
  "otp_code": "1234"
}
```

**תגובה:**
```json
{
  "success": true,
  "message": "העגלה הוקצתה בהצלחה. אנא החזר עד 14:30",
  "cart": { ... },
  "rental_id": 15,
  "expected_return": "2025-10-23T14:30:00"
}
```

---

### 2. היסטוריית השכרות

#### כל ההשכרות
```http
GET /rentals/history?limit=100
```

#### השכרות של משתמש ספציפי
```http
GET /rentals/history?phone=0501234567&limit=50
```

**תגובה:**
```json
{
  "rentals": [
    {
      "rental_id": 15,
      "cart_id": 3,
      "user_phone": "0501234567",
      "locker_id": 2,
      "start_time": "2025-10-23T12:30:00",
      "expected_return": "2025-10-23T14:30:00",
      "actual_return": "2025-10-23T14:15:00",
      "status": "returned",
      "notes": null
    }
  ],
  "total_count": 127,
  "active_count": 3,
  "late_count": 1
}
```

---

### 3. השכרות פעילות
```http
GET /rentals/active
```

---

### 4. השכרות שבאיחור
```http
GET /rentals/overdue
```

**תגובה:**
```json
[
  {
    "rental_id": 18,
    "cart_id": 5,
    "user_phone": "0521112233",
    "expected_return": "2025-10-23T12:00:00",
    "status": "overdue",
    "time_late": "01:45:30"
  }
]
```

---

### 5. ההשכרה שלי (למשתמש)
```http
GET /rentals/my-rental?phone=0501234567
```

**תגובה:**
```json
{
  "rental": { ... },
  "is_late": false,
  "time_remaining": "0:45:12",
  "duration": "1:14:48"
}
```

---

### 6. סטטיסטיקות
```http
GET /rentals/stats/summary
```

**תגובה:**
```json
{
  "total_rentals": 234,
  "active_rentals": 5,
  "overdue_rentals": 2,
  "late_returns": 15
}
```

---

### 7. סטטוס Monitor
```http
GET /rentals/monitor/status
```

**תגובה:**
```json
{
  "running": true,
  "check_interval": 5,
  "controller_connected": true,
  "database_path": "data/rentals.db"
}
```

---

## 🔄 תהליך מלא - End to End

### שלב 1: משתמש לוקח עגלה

```
1. משתמש: POST /auth/request-otp → קבלת קוד SMS
2. משתמש: POST /carts/assign → אימות קוד
3. מערכת:
   ✅ בדיקת OTP
   ✅ בדיקה שאין לו עגלה פעילה
   ✅ מציאת עגלה זמינה
   ✅ פתיחת מנעול דרך RS485
   ✅ יצירת rental record ב-DB:
      - start_time = NOW
      - expected_return = NOW + 120 דקות
      - status = active
   ✅ שליחת SMS אישור
4. משתמש מקבל עגלה
```

### שלב 2: Monitor פועל ברקע

```
כל 5 שניות, ה-Monitor בודק:

1. קריאת סטטוס מהבקר CU16 (GET_ALL_STATUS)
2. לכל rental פעיל:
   - בדיקה: האם יש עגלה במנעול?
   - בדיקה: האם המנעול נעול?

3. אם כן → עגלה הוחזרה!
   ✅ עדכון rental:
      - actual_return = NOW
      - status = returned (או returned_late אם איחר)
   ✅ עדכון cart:
      - status = available
      - assigned_to = None
   ✅ לוג: "Cart 3 returned by 0501234567 (duration: 1:35:22, late: false)"

4. בדיקת איחורים:
   - אם NOW > expected_return וסטטוס עדיין active
   → סימון כ-overdue
```

### שלב 3: משתמש מחזיר עגלה

```
אופציה א' - זיהוי אוטומטי:
1. משתמש מכניס עגלה למנעול
2. Micro-switch מזהה → מנעול נסגר אוטומטית
3. Monitor מזהה (בבדיקה הבאה) → מעדכן סטטוס
4. עגלה זמינה למשתמש הבא

אופציה ב' - בדיקה ידנית:
1. משתמש: POST /carts/complete-return
2. מערכת בודקת מנעול בזמן אמת
3. אם נסגר → מסיים את ההשכרה
```

---

## 🧪 בדיקות

### בדיקה מקומית (ללא חומרה)

```bash
# הפעלת שרת
python run_server.py

# בדיקת endpoints
curl http://localhost:8002/rentals/stats/summary
curl http://localhost:8002/rentals/monitor/status
```

### בדיקה עם חומרה

1. חבר בקר CU16 ל-COM port
2. ודא שה-port מוגדר נכון ב-`config/.env`
3. הרץ שרת
4. בדוק בלוגים:

```
INFO - RS485 controller connected
INFO - CU16 monitor service started
INFO - CU16 monitor loop started
DEBUG - Retrieved lock states from CU16 controller
```

---

## 📊 Logging

### רמות Logging

- **INFO**: אירועים רגילים (השכרה, החזרה)
- **WARNING**: איחורים, בעיות קלות
- **ERROR**: כשלים בתקשורת, שגיאות DB
- **DEBUG**: כל בדיקה של Monitor

### דוגמאות ללוגים

```
2025-10-23 12:30:15 - api.routers.carts - INFO - Cart assignment requested by 0501234567
2025-10-23 12:30:15 - utils.database - INFO - Created rental record 15 for cart 3 by 0501234567
2025-10-23 12:30:15 - api.routers.carts - INFO - Cart 3 assigned to 0501234567 (rental 15)

2025-10-23 14:25:30 - hardware.cu16_monitor - DEBUG - Retrieved lock states from CU16 controller
2025-10-23 14:25:30 - hardware.cu16_monitor - INFO - 🎉 Cart 3 returned detected (locker 2)
2025-10-23 14:25:30 - hardware.cu16_monitor - INFO - ✅ Cart 3 returned by 0501234567 (duration: 1:55:15, late: False)

2025-10-23 16:30:00 - hardware.cu16_monitor - WARNING - ⏰ Cart 5 is OVERDUE by 2:00:00 (user: 0521112233)
```

---

## ⚙️ הגדרות

### config/.env

```env
# זמן ברירת מחדל להשכרה (דקות)
# ניתן לשנות בקוד ב-carts.py:
DEFAULT_RENTAL_DURATION = 120  # 2 שעות

# תדירות בדיקה של Monitor (שניות)
# ניתן לשנות ב-dependencies.py:
check_interval=5
```

---

## 🔧 Troubleshooting

### Monitor לא פועל

```bash
# בדוק סטטוס
curl http://localhost:8002/rentals/monitor/status

# בדוק לוגים
tail -f logs/cartwise.log | grep "monitor"
```

**אם `running: false`:**
- Monitor לא התחיל בהצלחה
- בדוק שגיאות בלוגים בזמן startup

### Database לא נוצר

**בעיה:** `FileNotFoundError: data/rentals.db`

**פתרון:**
```bash
mkdir data
# השרת יצור אוטומטית את ה-DB בהרצה הבאה
```

### החזרות לא מזוהות

**בעיה:** Monitor לא מזהה החזרות

**בדיקות:**
1. RS485 מחובר? `curl http://localhost:8002/health`
2. Monitor רץ? `curl http://localhost:8002/rentals/monitor/status`
3. לוגים: `tail -f logs/cartwise.log | grep "Cart returned"`

---

## 📈 שיפורים עתידיים

- [ ] שליחת SMS תזכורת לפני תום הזמן
- [ ] שליחת SMS אזהרה על איחור
- [ ] דשבורד למנהל עם סטטיסטיקות
- [ ] ייצוא נתונים ל-Excel/CSV
- [ ] אפליקציית מובייל
- [ ] תמיכה במספר בקרי CU16 (עד 16 בקרים × 16 מנעולים = 256 עגלות!)

---

## 📞 תמיכה

אם יש בעיות, בדוק:
1. `logs/cartwise.log` - לוגים מפורטים
2. `data/rentals.db` - האם קיים?
3. Monitor status endpoint
4. Health endpoint

**כל הקוד מתועד במלואו עם Docstrings!**

בהצלחה! 🎉
