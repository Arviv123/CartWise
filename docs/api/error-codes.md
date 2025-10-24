# Error Codes Reference
## מדריך קודי שגיאה

<div dir="rtl">

## סקירה

כל ה-API endpoints מחזירים קודי שגיאה סטנדרטיים של HTTP עם הודעות מפורטות.

</div>

---

## HTTP Status Codes

### Success Codes (2xx)

| Code | Name | Description |
|------|------|-------------|
| 200 | OK | הבקשה הצליחה |
| 201 | Created | משאב נוצר בהצלחה |

### Client Error Codes (4xx)

| Code | Name | Description | Hebrew |
|------|------|-------------|---------|
| 400 | Bad Request | בקשה לא תקינה | בקשה שגויה |
| 401 | Unauthorized | אימות נכשל | לא מאומת |
| 404 | Not Found | משאב לא נמצא | לא נמצא |

### Server Error Codes (5xx)

| Code | Name | Description | Hebrew |
|------|------|-------------|---------|
| 500 | Internal Server Error | שגיאת שרת | שגיאה פנימית |

---

## Authentication Errors

### 401 - Invalid OTP

```json
{
  "detail": "קוד שגוי או פג תוקף"
}
```

**Causes:**
- OTP code incorrect
- OTP expired (> 5 minutes)
- OTP already used

**Solution:**
Request new OTP code

---

### 401 - Token Expired

```json
{
  "detail": "טוקן פג תוקף"
}
```

**Causes:**
- Auth token older than 30 days
- Token revoked

**Solution:**
Re-authenticate with OTP

---

### 500 - SMS Error

```json
{
  "detail": "שגיאה בשליחת SMS: connection timeout"
}
```

**Causes:**
- SMS provider unavailable
- Network error
- Invalid phone number

**Solution:**
- Check network connection
- Verify phone number format
- Try again

---

## Cart Errors

### 400 - Already Has Active Cart

```json
{
  "detail": "יש לך כבר עגלה פעילה (מספר 2). החזר אותה לפני שאתה לוקח עגלה חדשה."
}
```

**Causes:**
- User already has an active rental

**Solution:**
- Return current cart first
- Or use `/rentals/force-complete/{rental_id}` (admin)

---

### 404 - No Carts Available

```json
{
  "detail": "אין עגלות זמינות כרגע"
}
```

**Causes:**
- All carts are in use
- All carts in maintenance

**Solution:**
- Wait for cart to be returned
- Check `/rentals/active` to see when carts will be available

---

### 404 - Cart Not Found

```json
{
  "detail": "עגלה לא נמצאה"
}
```

**Causes:**
- Invalid cart_id
- Cart doesn't exist

**Solution:**
- Check valid cart IDs with `/carts`
- Use cart_id 1-5

---

### 404 - No Available Locks

```json
{
  "detail": "אין מנעולים פנויים להחזרה כרגע"
}
```

**Causes:**
- All return lockers occupied
- System full

**Solution:**
- Wait for a locker to become available
- Contact support

---

## Rental Errors

### 404 - No Active Rental

```json
{
  "detail": "לא נמצאה עגלה פעילה (No active rental found)"
}
```

**Causes:**
- User has no active rental
- Rental already completed

**Solution:**
- Check rental status with `/rentals/my-rental`
- Assign new cart with `/carts/assign`

---

### 404 - Rental Not Found

```json
{
  "detail": "Rental not found"
}
```

**Causes:**
- Invalid rental_id
- Rental doesn't exist

**Solution:**
- Check rental history with `/rentals/history`
- Verify rental_id

---

### 500 - Internal Error - Cart Not Found

```json
{
  "detail": "שגיאה פנימית - עגלה לא נמצאה (Internal error - cart not found)"
}
```

**Causes:**
- Database inconsistency
- Cart deleted but rental exists

**Solution:**
- Use `/rentals/force-complete/{rental_id}`
- Contact support

---

## Error Response Format

כל שגיאות מחזירות JSON בפורמט הבא:

```json
{
  "detail": "הודעת שגיאה בעברית ואנגלית"
}
```

Or for validation errors:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "phone"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

## Common Error Patterns

### Pattern 1: Phone Number Validation

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "phone"],
      "msg": "String should have at least 10 characters"
    }
  ]
}
```

**Solution:** Phone must be exactly 10 digits (e.g., "0501234567")

---

### Pattern 2: Missing Authorization

```json
{
  "detail": "Not authenticated"
}
```

**Solution:** Add `Authorization: Bearer TOKEN` header

---

### Pattern 3: Invalid Request Body

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body"],
      "msg": "Field required"
    }
  ]
}
```

**Solution:** Check request body format matches API spec

---

## Error Handling Examples

### JavaScript Example:

```javascript
async function handleApiCall() {
  try {
    const response = await fetch('/carts/assign', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: '0501234567', otp_code: '1234' })
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle specific error codes
      switch (response.status) {
        case 400:
          if (data.detail.includes('יש לך כבר עגלה')) {
            alert('יש לך עגלה פעילה. החזר אותה קודם.');
            redirectToReturn();
          }
          break;

        case 401:
          alert('קוד שגוי. נסה שוב.');
          break;

        case 404:
          if (data.detail.includes('אין עגלות זמינות')) {
            alert('אין עגלות זמינות כרגע. נסה שוב מאוחר יותר.');
          }
          break;

        case 500:
          alert('שגיאת שרת. אנא נסה שוב.');
          console.error('Server error:', data.detail);
          break;

        default:
          alert('שגיאה לא צפויה');
      }

      throw new Error(data.detail);
    }

    return data;

  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
```

### Python Example:

```python
import requests
from requests.exceptions import RequestException

def handle_api_call(phone, otp_code):
    try:
        response = requests.post(
            'http://localhost:8002/carts/assign',
            json={'phone': phone, 'otp_code': otp_code}
        )

        # Raise exception for error status codes
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_data = e.response.json()
        detail = error_data.get('detail', 'Unknown error')

        if status_code == 400:
            if 'יש לך כבר עגלה' in detail:
                print('Error: You already have an active cart')
                return None

        elif status_code == 401:
            print('Error: Invalid OTP code')
            return None

        elif status_code == 404:
            if 'אין עגלות זמינות' in detail:
                print('Error: No carts available')
                return None

        elif status_code == 500:
            print(f'Server error: {detail}')
            return None

        print(f'HTTP {status_code}: {detail}')
        return None

    except RequestException as e:
        print(f'Network error: {e}')
        return None
```

---

## Debugging Tips

### 1. Enable Debug Logs

Check `logs/cartwise.log` for detailed error information:

```bash
tail -f logs/cartwise.log
```

### 2. Use Interactive API Docs

Visit `http://localhost:8002/docs` to test endpoints interactively

### 3. Check Request Format

Verify your request matches the API specification:

```bash
# Good request
curl -X POST http://localhost:8002/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "0501234567"}'

# Bad request (missing Content-Type)
curl -X POST http://localhost:8002/auth/request-otp \
  -d '{"phone": "0501234567"}'
```

### 4. Validate Phone Number Format

Phone must be:
- ✅ Exactly 10 digits
- ✅ Start with 05
- ✅ String format (not number)

```json
// ✅ Good
{"phone": "0501234567"}

// ❌ Bad
{"phone": "050-123-4567"}  // Has dashes
{"phone": "501234567"}      // Missing leading 0
{"phone": 501234567}        // Number instead of string
```

---

**Version:** 1.0.0
**Last Updated:** 2025-10-23
