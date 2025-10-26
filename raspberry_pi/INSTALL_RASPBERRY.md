# התקנת Raspberry Pi - גרסה מינימלית
## Minimal Raspberry Pi Installation (Agent Only)

---

## 🎯 מה הרספברי עושה?

הרספברי הוא **רק סוכן פשוט** שמקשר בין הענן ל-RS485:

```
הענן אומר: "פתח מנעול 3"
   ↓
הרספברי מקבל פקודה
   ↓
הרספברי שולח ל-RS485
   ↓
המנעול נפתח
   ↓
הרספברי מדווח: "נפתח בהצלחה!"
```

**זה הכל!** 🎉

---

## 📦 מה להתקין על הרספברי?

### רק 3 קבצים!

1. `local_agent.py` - הסוכן המקומי
2. `webhook_support.py` - תמיכה ב-webhooks (אופציונלי)
3. `rs485.py` - קוד RS485

---

## 🚀 התקנה מהירה

### שלב 1: הורד את הקבצים

```bash
# צור תיקייה
mkdir -p ~/cartwise_agent
cd ~/cartwise_agent

# הורד את הקבצים הדרושים
wget https://raw.githubusercontent.com/Arviv123/CartWise/main/raspberry_pi/local_agent.py
wget https://raw.githubusercontent.com/Arviv123/CartWise/main/raspberry_pi/webhook_support.py
wget https://raw.githubusercontent.com/Arviv123/CartWise/main/raspberry_pi/minimal_requirements.txt

# צור תיקיית hardware
mkdir -p hardware
cd hardware
wget https://raw.githubusercontent.com/Arviv123/CartWise/main/src/hardware/rs485.py
cd ..

# צור __init__.py ריק
touch hardware/__init__.py
```

### שלב 2: התקן Python packages

```bash
# רק 2 חבילות!
pip3 install -r minimal_requirements.txt
```

או ידנית:
```bash
pip3 install pyserial requests
```

### שלב 3: הגדר הרשאות Serial

```bash
sudo usermod -a -G dialout $USER
# התנתק והתחבר מחדש
```

### שלב 4: הרץ!

```bash
python3 local_agent.py \
    --cloud-url https://cartwise-cloud.onrender.com \
    --branch-id branch_001 \
    --api-key YOUR_API_KEY \
    --serial-port /dev/ttyUSB0 \
    --baudrate 19200
```

**עם Webhook (אופציונלי):**

```bash
python3 local_agent.py \
    --cloud-url https://cartwise-cloud.onrender.com \
    --branch-id branch_001 \
    --api-key YOUR_API_KEY \
    --serial-port /dev/ttyUSB0 \
    --webhook-url https://your-modal-app.modal.host/api/functions/cartwiseWebhook
```

---

## 📂 מבנה התיקייה (מינימלי!)

```
~/cartwise_agent/
├── local_agent.py          # הסוכן המקומי
├── webhook_support.py      # webhooks (אופציונלי)
├── minimal_requirements.txt
└── hardware/
    ├── __init__.py         # קובץ ריק
    └── rs485.py            # קוד RS485
```

**זה הכל!** 4 קבצים בלבד!

---

## ⚙️ הפעלה אוטומטית

### systemd service (Linux):

```bash
sudo nano /etc/systemd/system/cartwise-agent.service
```

הכנס:

```ini
[Unit]
Description=CartWise Local Agent
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/cartwise_agent
ExecStart=/usr/bin/python3 local_agent.py --cloud-url https://cartwise-cloud.onrender.com --branch-id branch_001 --api-key YOUR_KEY --serial-port /dev/ttyUSB0 --baudrate 19200
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

הפעל:

```bash
sudo systemctl enable cartwise-agent
sudo systemctl start cartwise-agent
sudo systemctl status cartwise-agent
```

---

## 🪟 Windows (המחשב המרוחק)

### הורדה:

1. הורד ZIP: https://github.com/Arviv123/CartWise/archive/refs/heads/main.zip
2. פתח רק את התיקייה `raspberry_pi/`
3. העתק גם `src/hardware/rs485.py`

### התקנה:

```cmd
cd C:\cartwise_agent
pip install pyserial requests
```

### הרצה:

```cmd
python local_agent.py ^
    --cloud-url https://cartwise-cloud.onrender.com ^
    --branch-id branch_001 ^
    --api-key YOUR_KEY ^
    --serial-port COM3
```

### Auto-start (Windows):

1. צור `start_agent.bat`:
```batch
@echo off
cd C:\cartwise_agent
python local_agent.py --cloud-url https://cartwise-cloud.onrender.com --branch-id branch_001 --api-key YOUR_KEY --serial-port COM3
pause
```

2. העתק קיצור ל-`shell:startup` (`Win+R` → `shell:startup`)

---

## 🔧 פתרון בעיות

### "ModuleNotFoundError: No module named 'core'"

**זה תקין!** ה-`core` module רק בשרת הענן. הסוכן לא צריך אותו.

אם יש שגיאה - בדוק שהקוד עודכן לגרסה החדשה.

### "could not open port /dev/ttyUSB0"

```bash
# בדוק אילו פורטים יש
ls -l /dev/ttyUSB*
ls -l /dev/ttyS*

# בדוק הרשאות
groups  # ודא ש-dialout ברשימה
```

### "Failed to connect to cloud"

```bash
# בדוק אינטרנט
ping google.com

# בדוק URL
curl https://cartwise-cloud.onrender.com/docs
```

---

## 📊 לוגים

### Linux:

```bash
# Live logs
sudo journalctl -u cartwise-agent -f

# Last 100 lines
sudo journalctl -u cartwise-agent -n 100
```

### Windows:

הלוגים מודפסים לקונסולה. שמור לקובץ:

```cmd
python local_agent.py ... > agent.log 2>&1
```

---

## 🎯 סיכום

הרספברי הוא **פשוט מאוד**:

1. ✅ מקבל פקודות מהענן (polling כל שנייה)
2. ✅ מבצע unlock/lock על RS485
3. ✅ מדווח תוצאה חזרה
4. ✅ (אופציונלי) שולח webhooks

**כל השאר (API, Database, SMS, ממשק) - בענן!** ☁️

---

**גרסה:** 1.0.0
**תאריך:** 2025-10-25
**GitHub:** https://github.com/Arviv123/CartWise
