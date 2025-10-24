# 🚀 CartWise Pro - Start Here!
## מתחילים כאן - מדריך מהיר

---

## 📦 מה יש בפרויקט?

✅ **API מלא** - FastAPI עם כל הפונקציונליות
✅ **ממשק לקוח** - עיצוב מקצועי לשימוש עגלות
✅ **מערכת אימות** - OTP עם SMS (Inforu)
✅ **מעקב השכרות** - Database + היסטוריה
✅ **תיעוד מקיף** - Swagger UI + HTML
✅ **תמיכה ב-Docker** - מוכן לפריסה

---

## 🎯 איך מתחילים?

### סצנריו 1️⃣: רוצה לבדוק מקומית

```bash
# 1. התקן תלויות
pip install -r requirements.txt

# 2. הפעל
python run_server.py
```

הדפדפן יפתח אוטומטית: `http://localhost:8002`

---

### סצנריו 2️⃣: רוצה להעלות לאינטרנט

**קרא את המדריך המלא**: [`RENDER_SETUP_ANSWERS.md`](RENDER_SETUP_ANSWERS.md)

**תמצית**:
1. העלה ל-GitHub
2. צור Web Service ב-Render.com
3. בחר **Docker** כ-Environment
4. הוסף Environment Variables
5. Deploy!

**מדריך צעד-אחר-צעד**: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)

---

### סצנריו 3️⃣: רוצה ליצור Dashboard

**קרא את הפרומפט**: [`DASHBOARD_PROMPT.md`](DASHBOARD_PROMPT.md)

**איך?**
1. פתח את `DASHBOARD_PROMPT.md`
2. העתק את כל התוכן
3. הדבק ב-Claude או ChatGPT
4. קבל Dashboard מלא!

---

## 📚 תיעוד

### תיעוד API:
- **Swagger UI**: `http://localhost:8002/docs`
- **HTML מקיף**: [`docs/api/API_Documentation.html`](docs/api/API_Documentation.html)
- **Markdown**:
  - [`docs/api/authentication.md`](docs/api/authentication.md)
  - [`docs/api/carts.md`](docs/api/carts.md)
  - [`docs/api/rentals.md`](docs/api/rentals.md)
  - [`docs/api/error-codes.md`](docs/api/error-codes.md)

---

## 🔑 קבצי הגדרה חשובים

### 1. `.env` (צור אותו!)
```bash
cp .env.example .env
```

ערוך:
```env
DEMO_MODE=true
INFORU_USERNAME=your_username
INFORU_PASSWORD=your_password
```

### 2. `Dockerfile`
כבר מוכן! משמש ל-Docker deployment.

### 3. `requirements.txt`
כל התלויות של Python.

---

## 📖 קריאה מומלצת

| מסמך | מתי לקרוא |
|------|----------|
| [`README.md`](README.md) | סקירה כללית |
| [`RENDER_SETUP_ANSWERS.md`](RENDER_SETUP_ANSWERS.md) | לפני העלאה ל-Render |
| [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) | מדריך פריסה מלא |
| [`DASHBOARD_PROMPT.md`](DASHBOARD_PROMPT.md) | ליצירת Dashboard |
| [`docs/api/`](docs/api/) | תיעוד API מפורט |

---

## 💡 טיפים מהירים

### הפעלה מהירה (Development)
```bash
python run_server.py
```

### בדיקת API
```bash
curl http://localhost:8002/carts
```

### צפייה בתיעוד
פתח דפדפן: `http://localhost:8002/docs`

---

## ❓ שאלות נפוצות

### האם צריך חומרה?
לא! יש **Demo Mode** שעובד ללא RS485 או מנעולים.

### כמה עולה להעלות לאינטרנט?
- **Render Free**: $0 (עם Sleep)
- **Render Starter**: $7/חודש (מומלץ)

### איך משנים פורט?
ערוך `.env`:
```env
API_PORT=8080
```

### איך מוסיפים עגלות?
ערוך `src/database/carts_db.py` - מערך `self.carts`

---

## 🎯 Quick Start Checklist

- [ ] התקן Python 3.8+
- [ ] `pip install -r requirements.txt`
- [ ] צור `.env` מתוך `.env.example`
- [ ] `python run_server.py`
- [ ] פתח `http://localhost:8002`

---

## 🚀 Ready to Deploy?

קרא: [`RENDER_SETUP_ANSWERS.md`](RENDER_SETUP_ANSWERS.md)

---

## 📞 תמיכה

- **Issues**: https://github.com/Arviv123/CartWise/issues
- **Email**: support@cartwise.com

---

**🎉 בהצלחה!**

**Version:** 1.0.0
**Last Updated:** 2025-10-24
