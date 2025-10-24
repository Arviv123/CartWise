# Render.com Setup - תשובות מהירות
## מה למלא בטופס יצירת Web Service

---

## 📝 הטופס המלא - תשובות

### ✅ Name
```
CartWise-API
```
**הסבר**: השם של השירות שלך. זה ייצור URL כמו `https://cartwise-api.onrender.com`

---

### ✅ Project (אופציונלי)
```
(השאר ריק)
```
**הסבר**: Projects הם לארגון מספר שירותים ביחד. לא צריך לשימוש ראשוני.

---

### ✅ Environment
```
Docker
```
⚠️ **חשוב מאוד**: בחר **Docker** ולא Python!

**למה?** כי יצרנו `Dockerfile` מיוחד שמכיל את כל ההגדרות הנכונות.

---

### ✅ Branch
```
main
```
**הסבר**: הבranch מ-GitHub שממנו לעשות deploy. הקוד שלך ב-`main`.

---

### ✅ Region
```
Oregon (US West)
```
**אלטרנטיבות**:
- Frankfurt (Europe Central) - קרוב יותר לישראל
- Singapore (Southeast Asia)
- Ohio (US East)

**המלצה**: Oregon בסדר. אם תרצה ביצועים מעט יותר טובים בישראל, בחר Frankfurt.

---

### ✅ Root Directory
```
(השאר ריק!)
```
**הסבר**: משמש למונorepos. הפרויקט שלך בroot, אז לא צריך.

---

### ✅ Dockerfile Path
```
./Dockerfile
```
או פשוט:
```
Dockerfile
```
**הסבר**: הנתיב לקובץ ה-Dockerfile (שיצרנו). הוא בroot של הפרויקט.

---

### ✅ Instance Type

#### לפיתוח / ניסיון:
```
☑️ Free - $0/month
   512 MB RAM
   0.1 CPU
```

**יתרונות**:
- ✅ חינם לחלוטין
- ✅ מספיק לפיתוח
- ✅ מספיק לבדיקות

**חסרונות**:
- ❌ נכנס ל-Sleep אחרי 15 דקות חוסר שימוש
- ❌ הבקשה הראשונה לוקחת 30-60 שניות להתעורר
- ❌ לא שומר Database בין deploys

---

#### לייצור (מומלץ):
```
☑️ Starter - $7/month
   512 MB RAM
   0.5 CPU
```

**יתרונות**:
- ✅ לא נכנס ל-Sleep
- ✅ תמיכה ב-Persistent Disk (Database נשמר!)
- ✅ SSH Access
- ✅ Zero Downtime Deploys

---

#### לשימוש אינטנסיבי:
```
☑️ Standard - $25/month
   2 GB RAM
   1 CPU
```

**יתרונות**:
- ✅ יותר זיכרון ו-CPU
- ✅ ביצועים טובים יותר
- ✅ תומך בעומסים גבוהים

---

**המלצה שלי**:
1. התחל עם **Free** לניסיון
2. אם הכל עובד טוב, שדרג ל-**Starter** ($7)
3. רק אם יש הרבה משתמשים, שדרג ל-**Standard**

---

## 🔧 Environment Variables

לחץ **"Add Environment Variable"** והוסף את השורות הבאות:

### משתנה 1:
```
Name:  API_HOST
Value: 0.0.0.0
```

### משתנה 2:
```
Name:  API_PORT
Value: 8002
```

### משתנה 3:
```
Name:  DEMO_MODE
Value: true
```

### משתנה 4:
```
Name:  INFORU_USERNAME
Value: YOUR_INFORU_USERNAME
```
⚠️ **החלף ב-username האמיתי שלך מ-Inforu!**

### משתנה 5:
```
Name:  INFORU_PASSWORD
Value: YOUR_INFORU_PASSWORD
```
⚠️ **החלף בסיסמה האמיתית שלך מ-Inforu!**

---

### משתנים אופציונליים (רק אם תרצה לשנות ברירות מחדל):

### משתנה 6 (אופציונלי):
```
Name:  OTP_EXPIRATION_MINUTES
Value: 5
```
**הסבר**: כמה זמן קוד ה-OTP תקף. ברירת מחדל: 5 דקות.

### משתנה 7 (אופציונלי):
```
Name:  RENTAL_DURATION_HOURS
Value: 2
```
**הסבר**: כמה זמן מותר ללקוח להחזיק עגלה. ברירת מחדל: 2 שעות.

### משתנה 8 (רק אם יש לך חומרה):
```
Name:  RS485_PORT
Value: /dev/ttyUSB0
```
**הסבר**: פורט של ה-RS485 adapter. **לא צריך אם DEMO_MODE=true**

### משתנה 9 (רק אם יש לך חומרה):
```
Name:  RS485_BAUDRATE
Value: 19200
```
**הסבר**: מהירות תקשורת RS485. **לא צריך אם DEMO_MODE=true**

---

## 🎬 אחרי מילוי הכל

1. גלול למטה
2. לחץ **"Deploy web service"**
3. המתן 2-5 דקות
4. תקבל URL: `https://cartwise-api.onrender.com` (או השם שבחרת)

---

## ✅ בדיקה שהכל עובד

### 1. פתח דפדפן וגש ל:
```
https://YOUR-APP-NAME.onrender.com/
```

תראה:
```json
{
  "status": "ok",
  "service": "CartWise Pro API",
  "version": "1.0.0"
}
```

### 2. גש לתיעוד:
```
https://YOUR-APP-NAME.onrender.com/docs
```

תראה Swagger UI מלא!

### 3. גש לממשק לקוח:
```
https://YOUR-APP-NAME.onrender.com/
```

תראה את הממשק המלא!

---

## 🐛 פתרון בעיות

### "Application failed to respond"
- ✅ בדוק ש-Environment הוא **Docker** (לא Python)
- ✅ בדוק ש-API_HOST הוא `0.0.0.0`
- ✅ בדוק ש-API_PORT הוא `8002`

### "Build failed"
- ✅ בדוק ש-Dockerfile Path הוא `./Dockerfile`
- ✅ בדוק שה-Dockerfile קיים ב-GitHub
- ✅ צפה ב-Logs לשגיאה המדויקת

### "Service unavailable"
- ✅ זה נורמלי ב-Free tier בהתעוררות ראשונה (30-60 שניות)
- ✅ רענן את הדף אחרי דקה

---

## 📋 Checklist מהיר

לפני Deploy, וודא:
- [ ] הקוד ב-GitHub מעודכן
- [ ] Dockerfile קיים
- [ ] .gitignore לא כולל .env (רק .env.example)
- [ ] Environment Variables מולאו (במיוחד Inforu!)

---

## 🎉 זהו!

אחרי שה-Deploy מסתיים, המערכת שלך זמינה באינטרנט!

**קישורים חשובים**:
- Dashboard שלך ב-Render: https://dashboard.render.com
- GitHub Repo: https://github.com/Arviv123/CartWise
- מדריך מלא: ראה `DEPLOYMENT_GUIDE.md`

---

**Version:** 1.0.0
**Last Updated:** 2025-10-24
