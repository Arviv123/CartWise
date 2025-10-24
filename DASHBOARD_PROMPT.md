# CartWise Pro - Dashboard Creation Prompt
## פרומפט ליצירת דשבורד ניהול מקיף

---

## 🎯 הוראות לבינה המלאכותית

צור לי **דשבורד ניהול מקיף** עבור מערכת CartWise Pro - מערכת השכרת עגלות קניות חכמה.

---

## 📋 דרישות כלליות

### טכנולוגיות מומלצות:
- **Frontend Framework**: React 18+ עם TypeScript
- **Styling**: Tailwind CSS + Shadcn/ui components
- **State Management**: React Query (TanStack Query) או Zustand
- **Charts**: Recharts או Chart.js
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Date Handling**: date-fns או dayjs

### מבנה הפרויקט:
```
cartwise-dashboard/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── DashboardLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Header.tsx
│   │   ├── dashboard/
│   │   │   ├── StatisticsCards.tsx
│   │   │   ├── ActiveRentalsTable.tsx
│   │   │   ├── OverdueRentalsTable.tsx
│   │   │   └── RentalChartsSection.tsx
│   │   ├── carts/
│   │   │   ├── CartsStatusGrid.tsx
│   │   │   └── CartDetailsModal.tsx
│   │   ├── rentals/
│   │   │   ├── RentalHistoryTable.tsx
│   │   │   └── RentalDetailsModal.tsx
│   │   └── common/
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorAlert.tsx
│   │       └── StatusBadge.tsx
│   ├── services/
│   │   └── api.ts
│   ├── hooks/
│   │   ├── useRentals.ts
│   │   ├── useCarts.ts
│   │   └── useStatistics.ts
│   ├── types/
│   │   └── api.types.ts
│   └── App.tsx
├── package.json
└── README.md
```

---

## 🔌 פרטי חיבור ל-API

### כתובת ה-API:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://YOUR-APP-NAME.onrender.com';
```

⚠️ **חשוב**: כתובת ה-API תתקבל אחרי העלאה ל-Render.com

### Authentication:
המערכת לא דורשת אימות למטרות ניהול (Dashboard הוא admin panel).
אם תרצה להוסיף אימות, תוכל להוסיף Basic Auth או API Key.

---

## 📡 API Endpoints לשימוש

### 1. סטטיסטיקות כלליות
```http
GET /rentals/stats/summary
```

**Response:**
```json
{
  "total_rentals": 150,
  "active_rentals": 3,
  "returned_rentals": 142,
  "overdue_rentals": 5,
  "late_returns": 12,
  "average_duration_minutes": 95,
  "most_used_cart": 2
}
```

---

### 2. רשימת עגלות
```http
GET /carts
```

**Response:**
```json
[
  {
    "cart_id": 1,
    "locker_id": 0,
    "status": "available",
    "assigned_to": null,
    "is_locked": true,
    "last_used": null
  },
  {
    "cart_id": 2,
    "locker_id": 1,
    "status": "in_use",
    "assigned_to": "0501234567",
    "is_locked": false,
    "last_used": "2025-10-23T14:30:00"
  }
]
```

**Status Values:**
- `available` - עגלה זמינה (ירוק)
- `in_use` - עגלה בשימוש (כחול)
- `maintenance` - עגלה בתחזוקה (אדום)

---

### 3. השכרות פעילות
```http
GET /rentals/active
```

**Response:**
```json
[
  {
    "rental_id": 5,
    "cart_id": 1,
    "user_phone": "0501234567",
    "locker_id": 0,
    "start_time": "2025-10-23T16:00:00",
    "expected_return": "2025-10-23T18:00:00",
    "actual_return": null,
    "status": "active",
    "notes": null
  }
]
```

---

### 4. השכרות באיחור
```http
GET /rentals/overdue
```

**Response:**
```json
[
  {
    "rental_id": 3,
    "cart_id": 3,
    "user_phone": "0507654321",
    "locker_id": 2,
    "start_time": "2025-10-23T12:00:00",
    "expected_return": "2025-10-23T14:00:00",
    "actual_return": null,
    "status": "overdue",
    "notes": null
  }
]
```

---

### 5. היסטוריית השכרות
```http
GET /rentals/history?limit=100&phone={phone}
```

**Query Parameters:**
- `limit` (optional): מספר רשומות מקסימלי (ברירת מחדל: 100)
- `phone` (optional): סינון לפי מספר טלפון

**Response:**
```json
{
  "rentals": [
    {
      "rental_id": 1,
      "cart_id": 1,
      "user_phone": "0501234567",
      "locker_id": 0,
      "start_time": "2025-10-23T14:00:00",
      "expected_return": "2025-10-23T16:00:00",
      "actual_return": "2025-10-23T15:45:00",
      "status": "returned",
      "notes": null
    }
  ],
  "total_count": 150,
  "active_count": 3,
  "late_count": 1
}
```

**Status Values:**
- `active` - השכרה פעילה (כחול)
- `returned` - הוחזר בזמן (ירוק)
- `returned_late` - הוחזר באיחור (כתום)
- `overdue` - באיחור (אדום)
- `cancelled` - בוטל (אפור)

---

### 6. פרטי השכרה ספציפית
```http
GET /rentals/{rental_id}
```

**Response:**
```json
{
  "rental_id": 5,
  "cart_id": 1,
  "user_phone": "0501234567",
  "locker_id": 0,
  "start_time": "2025-10-23T16:00:00",
  "expected_return": "2025-10-23T18:00:00",
  "actual_return": null,
  "status": "active",
  "notes": null
}
```

---

### 7. סיום השכרה בכוח (Admin)
```http
POST /rentals/force-complete/{rental_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Rental 5 force completed"
}
```

⚠️ **Warning**: זה endpoint למטרות debug/admin בלבד!

---

### 8. סטטוס Monitor
```http
GET /rentals/monitor/status
```

**Response:**
```json
{
  "running": true,
  "check_interval": 5,
  "last_check": "2025-10-23T16:05:30"
}
```

---

## 🎨 דרישות עיצוב

### צבעים (Theme):
```css
/* Primary Colors */
--primary: #3B82F6 (כחול - Brand)
--success: #10B981 (ירוק - Success)
--warning: #F59E0B (כתום - Warning)
--danger: #EF4444 (אדום - Danger/Error)
--info: #06B6D4 (תכלת - Info)

/* Neutral Colors */
--gray-50: #F9FAFB
--gray-100: #F3F4F6
--gray-200: #E5E7EB
--gray-300: #D1D5DB
--gray-700: #374151
--gray-900: #111827
```

### פונטים:
- **Primary Font**: Inter או Rubik (תומך עברית)
- **Font Sizes**: טקסט 14-16px, כותרות 18-24px

### Layout:
- **Sidebar**: רוחב 240px, צמוד לצד שמאל
- **Main Content**: רספונסיבי, עם padding של 24px
- **Cards**: רדיוס עיגול 8px, shadow עדין

---

## 🖥️ דרישות תוכן - עמודים

### 1. Dashboard (דף הבית)

#### סקציה 1: Statistics Cards (4 כרטיסים במעלה)
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ 📊 סה"כ השכרות │ 🚗 עגלות פעילות│ ⚠️ באיחור      │ ⏱️ ממוצע זמן    │
│                 │                 │                 │                 │
│     150         │      3          │      5          │    95 דק'       │
│  +12 השבוע     │  מתוך 5        │  דורש טיפול   │                 │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

**Data Source**: `GET /rentals/stats/summary`

#### סקציה 2: Active Rentals Table
טבלה של השכרות פעילות כרגע:
- מספר השכרה
- מספר עגלה
- טלפון משתמש (מוסתר חלקית: 050-***-4567)
- זמן התחלה
- זמן צפוי להחזרה
- זמן נותר (מחושב בזמן אמת)
- אינדיקטור צבע (ירוק = בזמן, צהוב = עוד 15 דק', אדום = איחור)

**Data Source**: `GET /rentals/active`

**Features**:
- רענון אוטומטי כל 30 שניות
- עדכון זמן נותר בזמן אמת (ללא רענון)
- כפתור "סיים השכרה בכוח" (עם אישור)

#### סקציה 3: Charts
שני גרפים:

**גרף 1: השכרות ב-7 ימים אחרונים** (Bar Chart)
- ציר X: תאריכים
- ציר Y: מספר השכרות
- צבעים: ירוק = הושלם, כתום = באיחור

**גרף 2: שימוש בעגלות** (Pie Chart)
- כל עגלה עם אחוז השימוש שלה
- צבעים שונים לכל עגלה

---

### 2. Carts (עמוד עגלות)

#### סקציה 1: Carts Status Grid
תצוגת Grid של כל העגלות (5 עגלות):

```
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ 🛒 עגלה 1    │  │ 🛒 עגלה 2    │  │ 🛒 עגלה 3    │
│               │  │               │  │               │
│ ✅ זמינה      │  │ 🔵 בשימוש     │  │ ⚠️ באיחור     │
│               │  │               │  │               │
│ מנעול: 1     │  │ מנעול: 2     │  │ מנעול: 3     │
│               │  │ 050-***-4567 │  │ 050-***-7654 │
│               │  │               │  │               │
│ שימוש אחרון: │  │ עד: 18:30    │  │ איחור: 30 דק' │
│ 23/10 14:30  │  │               │  │               │
└───────────────┘  └───────────────┘  └───────────────┘
```

**Data Source**: `GET /carts`

**Colors by Status**:
- `available`: רקע ירוק בהיר
- `in_use`: רקע כחול בהיר
- `maintenance`: רקע אדום בהיר

**Click to View Details**:
- מודאל עם פרטי העגלה המלאים
- היסטוריית שימוש (10 השכרות אחרונות)

---

### 3. Rentals (עמוד השכרות)

#### סקציה 1: Filters Bar
פילטרים:
- חיפוש לפי טלפון
- סינון לפי סטטוס (הכל / פעילות / באיחור / הושלמו)
- טווח תאריכים (Date Range Picker)

#### סקציה 2: Rentals History Table
טבלה מפורטת עם:
- מספר השכרה
- מספר עגלה
- טלפון משתמש
- זמן התחלה
- זמן החזרה צפוי
- זמן החזרה בפועל
- משך (duration)
- סטטוס (badge צבעוני)

**Data Source**: `GET /rentals/history?limit=100`

**Features**:
- Pagination (20 רשומות בעמוד)
- מיון לפי כל עמודה
- Export ל-CSV
- לחיצה על שורה = פתיחת מודאל עם פרטים מלאים

---

### 4. Overdue (עמוד באיחור)

#### סקציה 1: Overdue Alert Banner
באנר אדום עם:
```
⚠️ יש כרגע 5 השכרות באיחור! דורש טיפול מיידי
```

#### סקציה 2: Overdue Rentals Table
טבלה מפורטת של השכרות באיחור:
- מספר השכרה
- מספר עגלה
- טלפון משתמש (עם כפתור "שלח תזכורת SMS")
- זמן התחלה
- זמן צפוי להחזרה
- איחור (כמה זמן)
- פעולות:
  - שלח SMS תזכורת
  - סיים השכרה בכוח
  - צור קריאת שירות

**Data Source**: `GET /rentals/overdue`

**Features**:
- רענון אוטומטי כל 60 שניות
- מיון לפי זמן איחור (הגדול ביותר למעלה)
- אינדיקטור חומרה (צהוב < 30 דק', כתום < 1 שעה, אדום > 1 שעה)

---

## 🔔 תכונות נוספות

### 1. Real-time Updates
- WebSocket או Polling כל 30 שניות
- עדכון אוטומטי של נתונים בלי רענון דף
- התראות Toast כשיש השכרה חדשה או איחור חדש

### 2. Notifications System
- התראה כשעגלה חדשה הושכרה
- התראה כשעגלה הוחזרה
- התראה כשעגלה נכנסת לאיחור

### 3. Search & Filter
- חיפוש גלובלי (בכל מקום בדשבורד)
- פילטרים מתקדמים
- שמירת פילטרים ב-localStorage

### 4. Export Data
- ייצוא טבלאות ל-CSV
- ייצוא דו"ח סטטיסטיקות ל-PDF
- ייצוא היסטוריה ל-Excel

### 5. Dark Mode
- תמיכה במצב כהה
- מעבר חלק בין מצבים
- שמירת העדפה ב-localStorage

---

## 📱 רספונסיביות

### Desktop (> 1024px):
- Sidebar תמיד פתוח
- טבלאות עם כל העמודות
- 4 כרטיסי סטטיסטיקה בשורה

### Tablet (768px - 1024px):
- Sidebar מתקפל לאייקונים
- טבלאות עם עמודות חשובות
- 2 כרטיסי סטטיסטיקה בשורה

### Mobile (< 768px):
- Sidebar כ-Drawer (נפתח מלחצן)
- טבלאות כ-Cards (vertical layout)
- 1 כרטיס סטטיסטיקה בשורה

---

## 🔧 קוד לדוגמה

### API Service (src/services/api.ts):

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const cartsAPI = {
  getAll: () => api.get('/carts'),
  getById: (id: number) => api.get(`/carts/${id}`),
};

export const rentalsAPI = {
  getStatistics: () => api.get('/rentals/stats/summary'),
  getActive: () => api.get('/rentals/active'),
  getOverdue: () => api.get('/rentals/overdue'),
  getHistory: (params?: { limit?: number; phone?: string }) =>
    api.get('/rentals/history', { params }),
  getById: (id: number) => api.get(`/rentals/${id}`),
  forceComplete: (id: number) => api.post(`/rentals/force-complete/${id}`),
  getMonitorStatus: () => api.get('/rentals/monitor/status'),
};

export default api;
```

---

### Types Definition (src/types/api.types.ts):

```typescript
export type CartStatus = 'available' | 'in_use' | 'maintenance';
export type RentalStatus = 'active' | 'returned' | 'returned_late' | 'overdue' | 'cancelled';

export interface Cart {
  cart_id: number;
  locker_id: number;
  status: CartStatus;
  assigned_to: string | null;
  is_locked: boolean;
  last_used: string | null;
}

export interface Rental {
  rental_id: number;
  cart_id: number;
  user_phone: string;
  locker_id: number;
  start_time: string;
  expected_return: string;
  actual_return: string | null;
  status: RentalStatus;
  notes: string | null;
}

export interface Statistics {
  total_rentals: number;
  active_rentals: number;
  returned_rentals: number;
  overdue_rentals: number;
  late_returns: number;
  average_duration_minutes: number;
  most_used_cart: number;
}

export interface RentalHistory {
  rentals: Rental[];
  total_count: number;
  active_count: number;
  late_count: number;
}

export interface MonitorStatus {
  running: boolean;
  check_interval: number;
  last_check: string;
}
```

---

### Custom Hook Example (src/hooks/useRentals.ts):

```typescript
import { useQuery } from '@tanstack/react-query';
import { rentalsAPI } from '../services/api';

export const useStatistics = () => {
  return useQuery({
    queryKey: ['statistics'],
    queryFn: () => rentalsAPI.getStatistics().then(res => res.data),
    refetchInterval: 30000, // Refresh every 30 seconds
  });
};

export const useActiveRentals = () => {
  return useQuery({
    queryKey: ['rentals', 'active'],
    queryFn: () => rentalsAPI.getActive().then(res => res.data),
    refetchInterval: 30000,
  });
};

export const useOverdueRentals = () => {
  return useQuery({
    queryKey: ['rentals', 'overdue'],
    queryFn: () => rentalsAPI.getOverdue().then(res => res.data),
    refetchInterval: 60000, // Refresh every 60 seconds
  });
};
```

---

## 🚀 הוראות סופיות

### שלב 1: צור את הפרויקט
```bash
npx create-react-app cartwise-dashboard --template typescript
cd cartwise-dashboard
npm install axios @tanstack/react-query tailwindcss date-fns lucide-react recharts
```

### שלב 2: הגדר את כתובת ה-API
צור קובץ `.env`:
```
REACT_APP_API_URL=https://YOUR-APP-NAME.onrender.com
```

### שלב 3: בנה את הקומפוננטות
לפי המבנה שתיארתי למעלה.

### שלב 4: טסט
```bash
npm start
```

### שלב 5: Deploy
```bash
npm run build
# העלה את תיקיית build/ ל-Vercel/Netlify/GitHub Pages
```

---

## ✅ Checklist תכונות

וודא שכל התכונות הבאות קיימות:

**Dashboard:**
- [ ] 4 כרטיסי סטטיסטיקות
- [ ] טבלת השכרות פעילות
- [ ] 2 גרפים (Bar + Pie)
- [ ] רענון אוטומטי

**Carts:**
- [ ] Grid עם כל העגלות
- [ ] אינדיקטור סטטוס צבעוני
- [ ] מודאל פרטי עגלה

**Rentals:**
- [ ] טבלת היסטוריה מלאה
- [ ] פילטרים (טלפון, סטטוס, תאריכים)
- [ ] Pagination
- [ ] מיון לפי עמודות

**Overdue:**
- [ ] באנר אזהרה
- [ ] טבלת איחורים
- [ ] כפתור "סיים בכוח"
- [ ] אינדיקטור חומרה

**General:**
- [ ] Sidebar ניווט
- [ ] Header עם חיפוש
- [ ] Dark mode
- [ ] רספונסיבי (Mobile/Tablet/Desktop)
- [ ] Toast notifications
- [ ] Error handling
- [ ] Loading states

---

## 🎨 Design Inspiration

התבסס על עיצובים אלה:
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Render Dashboard**: https://dashboard.render.com
- **Stripe Dashboard**: https://dashboard.stripe.com

---

## 📞 תמיכה

אם יש בעיות עם ה-API:
1. בדוק שה-API רץ: `https://YOUR-APP.onrender.com/`
2. בדוק תיעוד: `https://YOUR-APP.onrender.com/docs`
3. בדוק Logs ב-Render Dashboard

---

**Version:** 1.0.0
**Last Updated:** 2025-10-24

---

## 🎉 בהצלחה!

זהו פרומפט מקיף שמכסה את כל הדרוש ליצירת Dashboard מקצועי ומלא!
העבר את הפרומפט הזה לבינה מלאכותית (Claude/ChatGPT/etc.) והיא תיצור לך את הדשבורד המלא.
