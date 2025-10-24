# API Usage Examples
## דוגמאות שימוש ב-API

<div dir="rtl">

## סקירה

מסמך זה מכיל דוגמאות מלאות לשימוש ב-CartWise Pro API עם קטעי קוד מוכנים לשימוש.

</div>

---

## Complete User Journey

### Scenario: משתמש חדש לוקח עגלה ומחזיר אותה

```javascript
// ===== STEP 1: Request OTP =====
async function step1_requestOTP() {
  const phone = '0501234567';

  const response = await fetch('http://localhost:8002/auth/request-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone })
  });

  const data = await response.json();
  console.log('✅ OTP sent:', data.message);
  return phone;
}

// ===== STEP 2: Verify OTP & Get Token =====
async function step2_verifyOTP(phone, otpCode) {
  const response = await fetch('http://localhost:8002/auth/verify-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone: phone,
      otp_code: otpCode
    })
  });

  const data = await response.json();

  // Save token for future use
  localStorage.setItem('cartwise_auth_token', data.auth_token);

  console.log('✅ Token received:', data.auth_token.substring(0, 20) + '...');
  return data.auth_token;
}

// ===== STEP 3: Assign Cart =====
async function step3_assignCart(phone, token) {
  const response = await fetch('http://localhost:8002/carts/assign', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      phone: phone,
      otp_code: '0000'  // Dummy, using token
    })
  });

  const data = await response.json();
  console.log(`✅ Cart ${data.cart.cart_id} assigned!`);
  console.log(`⏰ Return by: ${data.expected_return}`);
  return data;
}

// ===== STEP 4: Initiate Return =====
async function step4_initiateReturn(phone) {
  const response = await fetch('http://localhost:8002/carts/initiate-return', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone })
  });

  const data = await response.json();
  console.log(`✅ Return cart to locker ${data.locker_number}`);
  return data.locker_number;
}

// ===== STEP 5: Complete Return =====
async function step5_completeReturn(phone) {
  const response = await fetch('http://localhost:8002/carts/complete-return', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone })
  });

  const data = await response.json();
  console.log('✅ Cart returned successfully!');
  return data;
}

// ===== RUN COMPLETE FLOW =====
async function completeFlow() {
  try {
    console.log('Starting complete user journey...\n');

    // Step 1: Request OTP
    const phone = await step1_requestOTP();
    console.log('\n📱 Check your SMS for OTP code\n');

    // In real app, wait for user input
    const otpCode = prompt('Enter OTP code:');

    // Step 2: Verify OTP
    const token = await step2_verifyOTP(phone, otpCode);
    console.log('\n');

    // Step 3: Assign cart
    await step3_assignCart(phone, token);
    console.log('\n🛒 Take your cart!\n');

    // Simulate usage time
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Step 4: Initiate return
    const lockerNumber = await step4_initiateReturn(phone);
    console.log(`\n🔄 Returning cart to locker ${lockerNumber}...\n`);

    // Simulate physical return
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Step 5: Complete return
    await step5_completeReturn(phone);
    console.log('\n✅ Journey complete!\n');

  } catch (error) {
    console.error('❌ Error:', error);
  }
}

// Run it!
completeFlow();
```

---

## Returning User Flow

### Scenario: משתמש חוזר עם טוקן שמור

```javascript
async function returningUserFlow() {
  const phone = '0501234567';

  // Get saved token
  const savedToken = localStorage.getItem('cartwise_auth_token');

  if (!savedToken) {
    console.log('No saved token, need to authenticate');
    return;
  }

  console.log('✅ Using saved token\n');

  // Request OTP (will skip if token valid)
  const response = await fetch('http://localhost:8002/auth/request-otp', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${savedToken}`
    },
    body: JSON.stringify({ phone })
  });

  const data = await response.json();

  if (data.already_authenticated) {
    console.log('✅ Already authenticated! Skipping OTP\n');

    // Directly assign cart
    const cartResponse = await fetch('http://localhost:8002/carts/assign', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${savedToken}`
      },
      body: JSON.stringify({
        phone: phone,
        otp_code: '0000'
      })
    });

    const cartData = await cartResponse.json();
    console.log(`✅ Cart ${cartData.cart.cart_id} assigned instantly! ⚡`);
  } else {
    console.log('Token expired, need new OTP');
  }
}

returningUserFlow();
```

---

## Python Complete Implementation

```python
import requests
import time
from typing import Optional

class CartWiseClient:
    """Complete CartWise API client."""

    def __init__(self, base_url='http://localhost:8002'):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.phone: Optional[str] = None

    def _headers(self):
        """Get headers with optional auth token."""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    # ===== Authentication =====

    def request_otp(self, phone: str) -> dict:
        """Request OTP code."""
        self.phone = phone
        response = requests.post(
            f'{self.base_url}/auth/request-otp',
            headers=self._headers(),
            json={'phone': phone}
        )
        return response.json()

    def verify_otp(self, otp_code: str) -> dict:
        """Verify OTP and get auth token."""
        response = requests.post(
            f'{self.base_url}/auth/verify-otp',
            json={
                'phone': self.phone,
                'otp_code': otp_code
            }
        )
        data = response.json()

        if 'auth_token' in data:
            self.token = data['auth_token']
            print(f'✅ Token saved: {self.token[:20]}...')

        return data

    # ===== Cart Operations =====

    def assign_cart(self) -> dict:
        """Assign cart to user."""
        response = requests.post(
            f'{self.base_url}/carts/assign',
            headers=self._headers(),
            json={
                'phone': self.phone,
                'otp_code': '0000'  # Using token
            }
        )
        return response.json()

    def initiate_return(self) -> dict:
        """Start cart return process."""
        response = requests.post(
            f'{self.base_url}/carts/initiate-return',
            json={'phone': self.phone}
        )
        return response.json()

    def complete_return(self) -> dict:
        """Complete cart return."""
        response = requests.post(
            f'{self.base_url}/carts/complete-return',
            json={'phone': self.phone}
        )
        return response.json()

    # ===== Rental Info =====

    def get_my_rental(self) -> Optional[dict]:
        """Get current active rental."""
        response = requests.get(
            f'{self.base_url}/rentals/my-rental',
            params={'phone': self.phone}
        )

        if response.status_code == 404:
            return None

        return response.json()

    def get_all_carts(self) -> list:
        """Get all carts status."""
        response = requests.get(f'{self.base_url}/carts')
        return response.json()

    # ===== High-level Flows =====

    def complete_flow(self, phone: str, otp_code: str):
        """Complete user journey."""
        print('🚀 Starting complete flow\n')

        # Step 1: Authentication
        print('1️⃣  Requesting OTP...')
        self.request_otp(phone)
        print('✅ OTP sent\n')

        # Step 2: Verify
        print('2️⃣  Verifying OTP...')
        self.verify_otp(otp_code)
        print('✅ Authenticated\n')

        # Step 3: Assign cart
        print('3️⃣  Assigning cart...')
        cart_data = self.assign_cart()
        cart_id = cart_data['cart']['cart_id']
        print(f'✅ Cart {cart_id} assigned\n')

        # Step 4: Simulate usage
        print('🛒 Using cart...')
        time.sleep(2)

        # Step 5: Return
        print('\n4️⃣  Initiating return...')
        return_data = self.initiate_return()
        locker = return_data['locker_number']
        print(f'✅ Return to locker {locker}\n')

        print('🔄 Returning cart...')
        time.sleep(1)

        # Step 6: Complete
        print('\n5️⃣  Completing return...')
        self.complete_return()
        print('✅ Return complete\n')

        print('🎉 Flow completed successfully!')

# ===== Usage =====

if __name__ == '__main__':
    client = CartWiseClient()

    # Option 1: Complete flow
    client.complete_flow('0501234567', '1234')

    # Option 2: Individual operations
    client = CartWiseClient()
    client.request_otp('0501234567')
    otp = input('Enter OTP: ')
    client.verify_otp(otp)

    # Now authenticated, can do operations
    cart = client.assign_cart()
    print(f'Got cart {cart["cart"]["cart_id"]}')

    # Check my rental
    rental = client.get_my_rental()
    if rental:
        print(f'Time remaining: {rental["time_remaining"]}')
```

---

## React Hook Example

```javascript
import { useState, useEffect } from 'react';

function useCartWise() {
  const [token, setToken] = useState(
    () => localStorage.getItem('cartwise_auth_token')
  );
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = 'http://localhost:8002';

  // Request OTP
  const requestOTP = async (phoneNumber) => {
    setLoading(true);
    setError(null);
    setPhone(phoneNumber);

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_URL}/auth/request-otp`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ phone: phoneNumber })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail);
      }

      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Verify OTP
  const verifyOTP = async (otpCode) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone,
          otp_code: otpCode
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail);
      }

      // Save token
      setToken(data.auth_token);
      localStorage.setItem('cartwise_auth_token', data.auth_token);

      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Assign cart
  const assignCart = async () => {
    setLoading(true);
    setError(null);

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_URL}/carts/assign`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          phone,
          otp_code: '0000'
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail);
      }

      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const logout = () => {
    setToken(null);
    localStorage.removeItem('cartwise_auth_token');
  };

  return {
    token,
    phone,
    loading,
    error,
    requestOTP,
    verifyOTP,
    assignCart,
    logout,
    isAuthenticated: !!token
  };
}

// ===== Usage in Component =====

function App() {
  const {
    token,
    loading,
    error,
    requestOTP,
    verifyOTP,
    assignCart,
    isAuthenticated
  } = useCartWise();

  const [step, setStep] = useState('phone'); // phone, otp, success

  const handleRequestOTP = async (phone) => {
    const result = await requestOTP(phone);

    if (result.already_authenticated) {
      // Skip OTP!
      const cart = await assignCart();
      setStep('success');
    } else {
      setStep('otp');
    }
  };

  const handleVerifyOTP = async (otp) => {
    await verifyOTP(otp);
    const cart = await assignCart();
    setStep('success');
  };

  return (
    <div>
      {step === 'phone' && (
        <PhoneInput onSubmit={handleRequestOTP} loading={loading} />
      )}

      {step === 'otp' && (
        <OTPInput onSubmit={handleVerifyOTP} loading={loading} />
      )}

      {step === 'success' && (
        <Success message="Cart assigned!" />
      )}

      {error && <Error message={error} />}
    </div>
  );
}
```

---

## Admin Dashboard Example

```python
import requests
import time
from datetime import datetime
from tabulate import tabulate

class AdminDashboard:
    """Admin dashboard for CartWise system."""

    def __init__(self, base_url='http://localhost:8002'):
        self.base_url = base_url

    def get_stats(self):
        """Get system statistics."""
        response = requests.get(f'{self.base_url}/rentals/stats/summary')
        return response.json()

    def get_active_rentals(self):
        """Get active rentals."""
        response = requests.get(f'{self.base_url}/rentals/active')
        return response.json()

    def get_overdue_rentals(self):
        """Get overdue rentals."""
        response = requests.get(f'{self.base_url}/rentals/overdue')
        return response.json()

    def get_all_carts(self):
        """Get all carts."""
        response = requests.get(f'{self.base_url}/carts')
        return response.json()

    def force_complete(self, rental_id):
        """Force complete a rental."""
        response = requests.post(
            f'{self.base_url}/rentals/force-complete/{rental_id}'
        )
        return response.json()

    def display_dashboard(self):
        """Display complete dashboard."""
        print('\n' + '=' * 70)
        print('CARTWISE ADMIN DASHBOARD'.center(70))
        print('=' * 70 + '\n')

        # Statistics
        stats = self.get_stats()
        print('📊 STATISTICS:')
        print(f'   Total Rentals:   {stats["total_rentals"]}')
        print(f'   Active Rentals:  {stats["active_rentals"]}')
        print(f'   Overdue:         {stats["overdue_rentals"]} ⚠️')
        print(f'   Late Returns:    {stats.get("late_returns", 0)}')
        print(f'   Avg Duration:    {stats.get("average_duration_minutes", 0)}min')
        print()

        # Carts Status
        carts = self.get_all_carts()
        available = [c for c in carts if c['status'] == 'available']
        in_use = [c for c in carts if c['status'] == 'in_use']

        print(f'🛒 CARTS STATUS:')
        print(f'   Available: {len(available)} / {len(carts)}')
        print(f'   In Use:    {len(in_use)} / {len(carts)}')
        print()

        # Active Rentals
        active = self.get_active_rentals()
        if active:
            print('🔵 ACTIVE RENTALS:')
            headers = ['ID', 'Cart', 'Phone', 'Started', 'Expected Return']
            rows = [
                [
                    r['rental_id'],
                    r['cart_id'],
                    r['user_phone'][-4:] + '****',
                    r['start_time'][11:16],
                    r['expected_return'][11:16]
                ]
                for r in active
            ]
            print(tabulate(rows, headers=headers, tablefmt='grid'))
            print()

        # Overdue Rentals
        overdue = self.get_overdue_rentals()
        if overdue:
            print('🔴 OVERDUE RENTALS:')
            headers = ['ID', 'Cart', 'Phone', 'Expected', 'Overdue']
            rows = [
                [
                    r['rental_id'],
                    r['cart_id'],
                    r['user_phone'][-4:] + '****',
                    r['expected_return'][11:16],
                    '⚠️ YES'
                ]
                for r in overdue
            ]
            print(tabulate(rows, headers=headers, tablefmt='grid'))
            print()

        print('=' * 70 + '\n')

    def monitor(self, interval=30):
        """Monitor system in real-time."""
        print('Starting real-time monitor...')
        print(f'Refreshing every {interval} seconds')
        print('Press Ctrl+C to stop\n')

        try:
            while True:
                self.display_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print('\nMonitor stopped.')

# ===== Usage =====

if __name__ == '__main__':
    dashboard = AdminDashboard()

    # Display once
    dashboard.display_dashboard()

    # Or monitor continuously
    # dashboard.monitor(interval=30)
```

---

**Version:** 1.0.0
**Last Updated:** 2025-10-23
