# CartWise Pro - Webhook Integration Guide
## מדריך שילוב Webhooks (Base44, Zapier, n8n)

---

## 🎯 למה Webhooks?

במקום לבדוק שינויים כל 10 שניות (בזבוז קרדיטים):

```
❌ Polling (בזבוז):
Dashboard ──[בדיקה כל 10 שניות]──> API
= 360 קריאות/שעה = 8,640 קריאות/יום 💸
```

עכשיו עם Webhooks (חסכון):

```
✅ Webhooks (חכם):
Local Agent ──[רק כשיש אירוע]──> Webhook ──> Dashboard
= 0 קריאות polling + רק אירועים אמיתיים! 💰
```

---

## 📦 התקנה

### שלב 1: שילוב Webhook Manager ב-Local Agent

ערוך את `raspberry_pi/local_agent.py`:

```python
# בתחילת הקובץ, הוסף:
from webhook_support import WebhookManager

# בתוך __init__ של LocalAgent:
def __init__(self, ..., webhook_url: Optional[str] = None):
    # ... קוד קיים ...

    # הוסף:
    self.webhook = WebhookManager(webhook_url)
    if webhook_url:
        logger.info(f"Webhooks enabled: {webhook_url}")
```

### שלב 2: שלח Webhooks על אירועים

ב-`execute_command` של LocalAgent, הוסף:

```python
def execute_command(self, command: dict):
    # ... קוד קיים ...

    if command_type == 'unlock':
        locker_id = params.get('locker_id')
        success = self.controller.unlock_cart(locker_id)

        # 🎉 שלח webhook!
        if success:
            self.webhook.cart_unlocked(
                cart_id=params.get('cart_id', locker_id + 1),
                locker_id=locker_id
            )

        result = {'locker_id': locker_id, 'unlocked': success}

    elif command_type == 'lock':
        locker_id = params.get('locker_id')
        success = self.controller.lock_cart(locker_id)

        # 🎉 שלח webhook!
        if success:
            self.webhook.cart_locked(
                cart_id=params.get('cart_id', locker_id + 1),
                locker_id=locker_id
            )

        result = {'locker_id': locker_id, 'locked': success}

    elif command_type == 'check_return':
        locker_id = params.get('locker_id')
        returned = self.controller.check_cart_returned(locker_id)

        # 🎉 שלח webhook!
        if returned:
            self.webhook.cart_returned(
                cart_id=params.get('cart_id', locker_id + 1),
                user_phone=params.get('user_phone', ''),
                rental_id=params.get('rental_id', 0),
                locker_id=locker_id
            )

        success = True
        result = {'locker_id': locker_id, 'returned': returned}
```

---

## 🔧 שימוש - Base44

### 1. צור Base44 Function

ב-Base44 Dashboard:
1. לך ל-**Code** → **Functions**
2. צור function חדשה: `cartwiseWebhook`
3. הכנס:

```javascript
export default async function cartwiseWebhook(req, res) {
  const { event_type, data, timestamp } = req.body;

  console.log(`[${timestamp}] Event: ${event_type}`, data);

  // עדכן את הטבלה בהתאם לאירוע
  switch (event_type) {
    case 'cart.assigned':
      await db.rentals.insert({
        cart_id: data.cart_id,
        user_phone: data.user_phone,
        start_time: data.start_time,
        status: 'active'
      });
      break;

    case 'cart.returned':
      await db.rentals.update({
        cart_id: data.cart_id,
        end_time: data.end_time,
        status: 'completed'
      });
      break;

    case 'cart.locked':
      await db.carts.update({
        cart_id: data.cart_id,
        is_locked: true
      });
      break;

    case 'cart.unlocked':
      await db.carts.update({
        cart_id: data.cart_id,
        is_locked: false
      });
      break;
  }

  res.json({ success: true });
}
```

### 2. קבל את ה-Webhook URL

העתק את ה-URL:
```
https://your-app.base44.app/api/functions/cartwiseWebhook
```

### 3. הרץ את ה-Agent עם Webhook

```bash
python raspberry_pi/local_agent.py \
    --cloud-url https://cartwise-cloud.onrender.com \
    --branch-id branch_001 \
    --api-key YOUR_API_KEY \
    --serial-port COM3 \
    --baudrate 19200 \
    --webhook-url https://your-app.base44.app/api/functions/cartwiseWebhook
```

---

## 🔗 שימוש - Zapier

### 1. צור Zap חדש

1. Trigger: **Webhooks by Zapier** → **Catch Hook**
2. העתק את ה-Webhook URL
3. Action: **Google Sheets** / **Airtable** / **Email** וכו'

### 2. הוסף ל-Agent

```bash
python raspberry_pi/local_agent.py \
    ... \
    --webhook-url https://hooks.zapier.com/hooks/catch/YOUR_ID/YOUR_SECRET
```

---

## 🔗 שימוש - n8n

### 1. צור Workflow

1. Add node: **Webhook**
2. העתק את ה-Webhook URL
3. הוסף nodes לעיבוד (Database, Email, Slack...)

### 2. הוסף ל-Agent

```bash
python raspberry_pi/local_agent.py \
    ... \
    --webhook-url https://your-n8n.app/webhook/cartwise
```

---

## 📡 Event Types

### cart.assigned
נשלח כשעגלה נלקחת.

```json
{
  "event_type": "cart.assigned",
  "data": {
    "cart_id": 1,
    "user_phone": "0501234567",
    "rental_id": 123,
    "locker_id": 0,
    "start_time": "2025-10-25T15:30:00"
  },
  "timestamp": "2025-10-25T15:30:00",
  "source": "cartwise_local_agent"
}
```

### cart.returned
נשלח כשעגלה מוחזרת.

```json
{
  "event_type": "cart.returned",
  "data": {
    "cart_id": 1,
    "user_phone": "0501234567",
    "rental_id": 123,
    "locker_id": 0,
    "end_time": "2025-10-25T17:00:00"
  },
  "timestamp": "2025-10-25T17:00:00",
  "source": "cartwise_local_agent"
}
```

### cart.locked / cart.unlocked
נשלח כשמנעול ננעל/נפתח.

```json
{
  "event_type": "cart.locked",
  "data": {
    "cart_id": 1,
    "locker_id": 0,
    "is_locked": true
  },
  "timestamp": "2025-10-25T17:00:05",
  "source": "cartwise_local_agent"
}
```

### cart.overdue
נשלח כשעגלה באיחור.

```json
{
  "event_type": "cart.overdue",
  "data": {
    "cart_id": 1,
    "user_phone": "0501234567",
    "rental_id": 123,
    "minutes_overdue": 30
  },
  "timestamp": "2025-10-25T18:00:00",
  "source": "cartwise_local_agent"
}
```

### lock.error
נשלח כשיש שגיאה בתקשורת.

```json
{
  "event_type": "lock.error",
  "data": {
    "cart_id": 1,
    "locker_id": 0,
    "error_type": "communication_error",
    "error_message": "No response from controller"
  },
  "timestamp": "2025-10-25T15:30:05",
  "source": "cartwise_local_agent"
}
```

---

## 🎨 דוגמאות שימוש

### Google Sheets Logging

**Zapier:**
1. Trigger: Webhook
2. Action: Google Sheets → Create Spreadsheet Row
3. Map fields:
   - Column A: `event_type`
   - Column B: `data__cart_id`
   - Column C: `data__user_phone`
   - Column D: `timestamp`

### Email Alerts

**Zapier/n8n:**
1. Trigger: Webhook
2. Filter: `event_type` = `cart.overdue`
3. Action: Gmail → Send Email
   - To: `admin@example.com`
   - Subject: `עגלה באיחור - {{data__cart_id}}`
   - Body: `עגלה {{data__cart_id}} באיחור של {{data__minutes_overdue}} דקות`

### Slack Notifications

**n8n:**
1. Webhook trigger
2. Slack → Send Message
   - Channel: `#cart-alerts`
   - Message: `:shopping_cart: עגלה {{data.cart_id}} נלקחת על ידי {{data.user_phone}}`

---

## 💰 חיסכון בקרדיטים

### לפני (Polling):
```
Dashboard checks API every 10 seconds:
= 6 calls/min × 60 min = 360 calls/hour
= 360 × 24 = 8,640 calls/day
= 259,200 calls/month

At $0.01/call = $2,592/month 💸
```

### אחרי (Webhooks):
```
Webhooks only on events:
= ~50 events/day (10 rentals × 5 events each)
= 1,500 events/month

At $0.01/event = $15/month 💰

SAVINGS: $2,577/month! 🎉
```

---

## 🔒 אבטחה

### 1. Webhook Secrets (מומלץ!)

בקרוב - אוסיף תמיכה ב-HMAC signature:

```python
webhook = WebhookManager(
    webhook_url="https://your-app/webhook",
    secret="your-secret-key"
)
```

הwebhook יכלול:
```
X-Webhook-Signature: sha256=abc123...
```

### 2. IP Whitelist

הגבל גישה לwebhook רק מה-IP של הרספברי.

### 3. HTTPS Only

תמיד השתמש ב-HTTPS webhooks!

---

## 🧪 בדיקה

### Test Webhook ידני:

```bash
curl -X POST https://your-app.base44.app/api/functions/cartwiseWebhook \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "cart.assigned",
    "data": {
      "cart_id": 1,
      "user_phone": "0501234567",
      "rental_id": 123,
      "locker_id": 0,
      "start_time": "2025-10-25T15:30:00"
    },
    "timestamp": "2025-10-25T15:30:00",
    "source": "test"
  }'
```

---

## 📊 ניטור

### Webhook Logs

ה-Agent מדפיס logs:

```
Webhook sent successfully to Primary: cart.assigned
Webhook sent successfully to Zapier: cart.returned
```

### שגיאות:

```
Webhook Primary returned 500: Internal Server Error
Webhook Primary timed out (attempt 1/3)
```

---

## 🎯 סיכום

✅ **0 קרדיטים לpolling** - רק webhooks
✅ **עדכונים מיידיים** - תוך שנייה
✅ **חיסכון עצום** - 99% פחות קריאות
✅ **גמיש** - תומך ב-Base44, Zapier, n8n, custom
✅ **אמין** - retry mechanism מובנה

**חיסכת אלפי שקלים! 💰🎉**

---

**גרסה:** 1.0.0
**תאריך:** 2025-10-25
**GitHub:** https://github.com/Arviv123/CartWise
