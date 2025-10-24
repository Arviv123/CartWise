# CartWise Pro API Documentation
## מערכת ניהול עגלות חכמות - תיעוד API

<div dir="rtl">

## תוכן עניינים

1. [סקירה כללית](#סקירה-כללית)
2. [התחברות והתקנה](#התחברות-והתקנה)
3. [אימות (Authentication)](#אימות)
4. [ניהול עגלות (Carts)](#ניהול-עגלות)
5. [ניהול השכרות (Rentals)](#ניהול-השכרות)
6. [קודי שגיאה](#קודי-שגיאה)
7. [דוגמאות שימוש](#דוגמאות-שימוש)

---

## סקירה כללית

CartWise Pro API היא REST API המספקת ממשק מלא לניהול מערכת השכרת עגלות קניות חכמות.

### מאפיינים עיקריים:
- ✅ אימות דו-שלבי (OTP) באמצעות SMS
- ✅ מערכת טוקנים לאימות מתמשך (30 יום)
- ✅ ניהול עגלות ומנעולים אלקטרוניים
- ✅ מעקב אחר השכרות פעילות
- ✅ התראות SMS אוטומטיות
- ✅ תמיכה ב-RS485 לבקרי CU16

### Base URL:
```
http://localhost:8002
```

### Content-Type:
```
application/json
```

---

## התחברות והתקנה

### דרישות מערכת:
- Python 3.8+
- FastAPI
- SQLite
- RS485 adapter (אופציונלי - למצב production)

### הפעלת השרת:
```bash
python run_server.py
```

השרת יעלה על: `http://0.0.0.0:8002`

### Interactive API Docs:
```
http://localhost:8002/docs
```

---

## אימות

### סקירה
המערכת משתמשת באימות דו-שלבי:
1. **OTP בפעם הראשונה** - קוד SMS חד-פעמי
2. **טוקן לאימות מתמשך** - תקף ל-30 יום

---

## Endpoints

</div>

**Full API documentation available in:**
- [Authentication API](./authentication.md)
- [Carts API](./carts.md)
- [Rentals API](./rentals.md)
- [Error Codes](./error-codes.md)
- [Examples](./examples.md)

---

## Quick Start

### 1. Request OTP
```bash
curl -X POST http://localhost:8002/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "0501234567"}'
```

### 2. Verify OTP & Get Token
```bash
curl -X POST http://localhost:8002/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "0501234567", "otp_code": "1234"}'
```

Response:
```json
{
  "success": true,
  "message": "קוד אומת בהצלחה",
  "phone": "0501234567",
  "auth_token": "abc123...",
  "token_expires_days": 30
}
```

### 3. Assign Cart (with token)
```bash
curl -X POST http://localhost:8002/carts/assign \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"phone": "0501234567", "otp_code": "0000"}'
```

---

## Support

For issues and questions:
- Check logs: `logs/cartwise.log`
- API Docs: `http://localhost:8002/docs`
- Contact: support@cartwise.com

---

**Version:** 1.0.0
**Last Updated:** 2025-10-23
