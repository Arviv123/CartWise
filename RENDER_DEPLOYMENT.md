# CartWise Pro - Render.com Deployment Guide
## מדריך העלאה ל-Render.com

---

## 🚀 שלבי הפריסה

### שלב 1: הכנת הקוד ב-GitHub

1. **העלה את הקוד ל-GitHub** (אם עדיין לא עשית):
```bash
cd C:\Users\חיים\CartWise-Pro
git init
git add .
git commit -m "Initial commit - CartWise Pro"
git remote add origin https://github.com/Arviv123/CartWise.git
git push -u origin main
```

---

### שלב 2: הגדרות ב-Render.com

#### מילוי הטופס:

**Name:**
```
CartWise-API
```

**Project:**
```
(אופציונלי - אפשר להשאיר ריק)
```

**Environment:**
```
Docker
```
*(חשוב! בחר Docker ולא Python)*

**Branch:**
```
main
```

**Region:**
```
Oregon (US West)
```
*(או כל אזור אחר שמתאים לך)*

**Root Directory:**
```
(השאר ריק)
```

**Dockerfile Path:**
```
./Dockerfile
```

**Instance Type:**
```
Free - $0/month
```
*(לשלב הניסיון - אפשר לשדרג אחר כך)*

⚠️ **שים לב**:
- Instance חינמי נכנס ל-Sleep אחרי 15 דקות של חוסר שימוש
- הבקשה הראשונה תיקח 30-60 שניות להתעורר
- לשימוש ייצור רציני, מומלץ Starter ($7/חודש) או Standard ($25/חודש)

---

### שלב 3: משתני סביבה (Environment Variables)

לחץ על **"Add Environment Variable"** והוסף את המשתנים הבאים:

#### משתנים חובה:

**1. API_HOST**
```
0.0.0.0
```

**2. API_PORT**
```
8002
```

**3. DEMO_MODE**
```
true
```
*(true = ללא חומרה, false = עם חומרת RS485)*

**4. INFORU_USERNAME**
```
YOUR_INFORU_USERNAME
```

**5. INFORU_PASSWORD**
```
YOUR_INFORU_PASSWORD
```

#### משתנים אופציונליים:

**6. OTP_EXPIRATION_MINUTES** (ברירת מחדל: 5)
```
5
```

**7. RENTAL_DURATION_HOURS** (ברירת מחדל: 2)
```
2
```

**8. RS485_PORT** (רק אם DEMO_MODE=false)
```
/dev/ttyUSB0
```

**9. RS485_BAUDRATE** (רק אם DEMO_MODE=false)
```
19200
```

---

### שלב 4: פריסה

1. לחץ על **"Deploy web service"** בתחתית הדף
2. המערכת תתחיל לבנות את ה-Docker Image
3. זה ייקח 2-5 דקות
4. כשהפריסה מסתיימת, תקבל URL כמו:
```
https://cartwise-api.onrender.com
```

---

## 🔗 גישה ל-API

אחרי הפריסה, ה-API שלך יהיה זמין ב:

```
https://YOUR-APP-NAME.onrender.com
```

### בדיקת סטטוס:

```bash
curl https://YOUR-APP-NAME.onrender.com/
```

תקבל:
```json
{
  "status": "ok",
  "service": "CartWise Pro API",
  "version": "1.0.0"
}
```

### תיעוד אינטראקטיבי:

```
https://YOUR-APP-NAME.onrender.com/docs
```

---

## 🎨 חיבור Dashboard

כשתיצור Dashboard, תצטרך לעדכן את כתובת ה-API:

### ב-JavaScript:
```javascript
const API_URL = 'https://YOUR-APP-NAME.onrender.com';
```

### ב-React:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://YOUR-APP-NAME.onrender.com';
```

---

## 📊 ניטור ו-Logs

### צפייה ב-Logs בזמן אמת:

1. היכנס ל-Render Dashboard
2. לחץ על השירות שלך
3. לחץ על **"Logs"**

### בדיקת בריאות השירות:

Render בודק אוטומטית ש-HTTP requests מחזירים 200 OK

---

## 🔄 עדכון הקוד

כשאתה עושה שינויים:

```bash
git add .
git commit -m "תיאור השינוי"
git push
```

Render יזהה את ה-Push אוטומטית ויעשה Deploy מחדש!

---

## ⚙️ הגדרות מתקדמות

### שינוי Instance Type:

Settings → Instance Type → בחר Starter/Standard/Pro

### הוספת Persistent Disk (לשמירת Database):

Settings → Disks → Add Disk
- Name: `cartwise-data`
- Mount Path: `/app/data`
- Size: 1GB (מספיק)

⚠️ **חשוב**: Persistent Disk זמין רק ל-Paid plans!

### הגדרת Health Check:

Settings → Health Check Path
```
/
```

---

## 🐛 פתרון בעיות נפוצות

### 1. השירות לא עולה

בדוק ב-Logs אם יש שגיאות:
- שגיאות Python → בדוק dependencies ב-requirements.txt
- שגיאות Docker → בדוק Dockerfile

### 2. "Application failed to respond"

- בדוק שה-PORT הוא 8002
- בדוק ש-API_HOST הוא 0.0.0.0

### 3. Database לא שומר מידע

- ב-Free tier, הדטה נמחקת כל deploy
- צריך Persistent Disk (Paid plan)
- **פתרון זמני**: השתמש ב-External DB (כמו Supabase)

### 4. SMS לא נשלחים

- בדוק ש-INFORU_USERNAME וסיסמה נכונים
- בדוק שיש אשראי ב-Inforu
- בדוק Logs לשגיאות SMS

---

## 💰 עלויות

| Plan | מחיר | זיכרון | CPU | Sleep? | Disk? |
|------|------|--------|-----|--------|-------|
| Free | $0 | 512MB | 0.1 | ✅ כן | ❌ לא |
| Starter | $7 | 512MB | 0.5 | ❌ לא | ✅ כן |
| Standard | $25 | 2GB | 1 | ❌ לא | ✅ כן |

**המלצה**:
- לפיתוח: Free
- לייצור: Starter ($7)
- לשימוש אינטנסיבי: Standard ($25)

---

## 🔐 אבטחה

### HTTPS

Render מספק HTTPS אוטומטית!

ה-API שלך מוגן עם Let's Encrypt SSL:
```
https://YOUR-APP-NAME.onrender.com ✅
```

### CORS

אם תצטרך לאפשר גישה מדומיין אחר, עדכן ב-`run_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-dashboard-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📱 בדיקה מהטלפון

אחרי הפריסה, תוכל לבדוק מכל מכשיר:

```bash
# מהדפדפן
https://YOUR-APP-NAME.onrender.com/docs

# מ-cURL
curl https://YOUR-APP-NAME.onrender.com/carts

# מ-Postman
GET https://YOUR-APP-NAME.onrender.com/carts
```

---

## ✅ Checklist לפני הפריסה

- [ ] הקוד ב-GitHub מעודכן
- [ ] Dockerfile קיים ותקין
- [ ] requirements.txt מעודכן
- [ ] משתני סביבה מוכנים (Inforu username/password)
- [ ] .env.example קיים (לא .env!)
- [ ] DEMO_MODE=true (אם אין חומרה)

---

## 🎉 סיימת!

ה-API שלך עכשיו זמין באינטרנט!

**URL לדוגמה:**
```
https://cartwise-api.onrender.com
```

**תיעוד:**
```
https://cartwise-api.onrender.com/docs
```

---

**Version:** 1.0.0
**Last Updated:** 2025-10-24
