# הגדרת CartWise Pro בלינוקס

## תיקונים שבוצעו למערכת לינוקס

### המערכת עכשיו תומכת אוטומטית בלינוקס!

הקוד עודכן ב-`src/core/config.py` כך שהוא מזהה אוטומטית את מערכת ההפעלה ומתאים את שם הפורט בהתאם.

## התקנה בלינוקס

### דרישות מקדימות
```bash
# התקנת Python 3.8+
sudo apt update
sudo apt install python3 python3-pip python3-venv

# התקנת כלי פיתוח (נדרש עבור חלק מהספריות)
sudo apt install build-essential
```

### התקנת המערכת

1. **העתק את התיקייה למחשב לינוקס**
   ```bash
   # העתק את כל התיקייה CartWise-Pro
   # אפשר באמצעות USB, SCP, או כל שיטה אחרת
   ```

2. **צור סביבה וירטואלית**
   ```bash
   cd CartWise-Pro
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **התקן תלויות**
   ```bash
   pip install -r requirements.txt
   ```

## הגדרת פורט RS485

### שלב 1: מציאת הפורט

```bash
# הצג את כל הפורטים הזמינים
ls -l /dev/tty*

# או השתמש ב-dmesg לראות מה זוהה
dmesg | grep tty

# או ב-Python
python3 -c "import serial.tools.list_ports; [print(p.device) for p in serial.tools.list_ports.comports()]"
```

תוצאה טיפוסית:
```
/dev/ttyUSB0
/dev/ttyACM0
```

### שלב 2: הגדרת הרשאות

```bash
# הוסף את המשתמש לקבוצת dialout
sudo usermod -a -G dialout $USER

# התנתק והתחבר מחדש, או הפעל:
newgrp dialout

# בדוק שההרשאות הוגדרו:
groups
# צריך להראות: ... dialout ...
```

### שלב 3: הגדרת קובץ .env

ערוך את `config/.env`:

**אופציה 1: השאר COM4 (מומלץ)**
```env
SERIAL_PORT=COM4
```
המערכת תהפוך את זה אוטומטית ל-`/dev/ttyCOM4`

**אופציה 2: שימוש ישיר בנתיב לינוקס**
```env
SERIAL_PORT=/dev/ttyUSB0
```

### שלב 4 (אופציונלי): יצירת קישור קבוע עם udev

אם אתה רוצה שהפורט תמיד יקרא `/dev/ttyCOM4`:

1. **מצא את מזהה הפורט**
   ```bash
   udevadm info -a -n /dev/ttyUSB0 | grep '{idVendor}\|{idProduct}\|{serial}'
   ```

2. **צור udev rule**
   ```bash
   sudo nano /etc/udev/rules.d/99-usb-serial.rules
   ```

3. **הוסף את השורה הבאה** (שנה את idVendor ו-idProduct בהתאם למה שמצאת):
   ```
   SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="ttyCOM4"
   ```

4. **טען מחדש את ה-rules**
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

5. **נתק וחבר מחדש את הבקר**

6. **בדוק**
   ```bash
   ls -l /dev/ttyCOM4
   ```

## הרצת השרת

```bash
# הפעל את הסביבה הוירטואלית
source venv/bin/activate

# הרץ את השרת
python3 run_server.py
```

## בדיקה

1. פתח דפדפן: `http://localhost:8002`
2. או בדוק את ה-API: `curl http://localhost:8002/health`

## Troubleshooting בלינוקס

### השרת לא מתחבר לפורט
```bash
# בדוק שהפורט קיים
ls -l /dev/ttyUSB0  # או /dev/ttyCOM4

# בדוק הרשאות
groups  # צריך להכיל dialout

# בדוק שאף תוכנה אחרת לא משתמשת בפורט
lsof | grep ttyUSB
```

### השרת קורס עם שגיאת Permission Denied
```bash
# פתרון מהיר (לא מומלץ לייצור)
sudo chmod 666 /dev/ttyUSB0

# פתרון נכון (מומלץ)
sudo usermod -a -G dialout $USER
newgrp dialout
```

### הפורט מתנתק
```bash
# בדוק לוגים של המערכת
dmesg | tail -30

# בדוק את הכבל והחיבור פיזית
```

### שינוי שם הפורט אחרי כל אתחול
- השתמש ב-udev rules (ראה שלב 4 למעלה)

## הפעלה אוטומטית עם systemd

אם אתה רוצה שהשרת יפעל אוטומטית בהפעלה:

1. **צור קובץ service**
   ```bash
   sudo nano /etc/systemd/system/cartwise.service
   ```

2. **הוסף את התוכן הבא** (שנה את הנתיבים):
   ```ini
   [Unit]
   Description=CartWise Pro Server
   After=network.target

   [Service]
   Type=simple
   User=YOUR_USERNAME
   WorkingDirectory=/path/to/CartWise-Pro
   Environment="PATH=/path/to/CartWise-Pro/venv/bin"
   ExecStart=/path/to/CartWise-Pro/venv/bin/python run_server.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **הפעל את ה-service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable cartwise.service
   sudo systemctl start cartwise.service

   # בדיקת סטטוס
   sudo systemctl status cartwise.service
   ```

## הבדלים בין Windows ללינוקס

| פיצ'ר | Windows | Linux |
|-------|---------|-------|
| שם פורט | COM4 | /dev/ttyUSB0 או /dev/ttyCOM4 |
| הרשאות | Run as Admin | קבוצת dialout |
| התקנת Python | python | python3 |
| pip | pip | pip3 |
| הפעלה | `python run_server.py` | `python3 run_server.py` |

## תמיכה

אם נתקלת בבעיות, בדוק את:
1. `logs/cartwise.log` - לוגים של האפליקציה
2. `dmesg | tail` - לוגים של המערכת
3. `journalctl -xe` - לוגים כלליים של systemd

בהצלחה! 🐧
