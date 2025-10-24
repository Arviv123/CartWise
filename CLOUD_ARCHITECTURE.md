# CartWise Pro - Cloud Multi-Tenant Architecture
## ארכיטקטורה ענן רב-סניפית

---

## 🎯 סקירה

מערכת CartWise Pro מורחבת לתמיכה ברשתות קמעונאיות מרובות (Chains) עם סניפים, כל סניף עם התקני Raspberry Pi שמתקשרים עם ענן מרכזי.

---

## 🏗️ ארכיטקטורת המערכת

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD BACKEND                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FastAPI   │  │  PostgreSQL  │  │     MQTT     │      │
│  │   Server    │  │   Database   │  │    Broker    │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘              │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTPS / MQTT
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
│  Branch A     │ │  Branch B     │ │  Branch C     │
│  ┌─────────┐  │ │  ┌─────────┐  │ │  ┌─────────┐  │
│  │ RPi #1  │  │ │  │ RPi #1  │  │ │  │ RPi #1  │  │
│  │ RS485   │  │ │  │ RS485   │  │ │  │ RS485   │  │
│  └─────────┘  │ │  └─────────┘  │ │  └─────────┘  │
│  ┌─────────┐  │ │  ┌─────────┐  │ │  ┌─────────┐  │
│  │ RPi #2  │  │ │  │ RPi #2  │  │ │  │ RPi #2  │  │
│  │ RS485   │  │ │  │ RS485   │  │ │  │ RS485   │  │
│  └─────────┘  │ │  └─────────┘  │ │  └─────────┘  │
└───────────────┘ └───────────────┘ └───────────────┘
```

---

## 📊 Data Model Hierarchy

```
Chain (רשת)
  └── Branch (סניף)
        ├── Device (רסברי פאי)
        │     └── Controller (בקר RS485)
        └── Cart (עגלה)
              └── Rental (השכרה)
```

---

## 🔄 Communication Flow

### 1. Device Registration
```
Raspberry Pi → POST /api/devices/register
              ← Device Token (JWT)
```

### 2. Heartbeat
```
Raspberry Pi → POST /api/devices/heartbeat (כל 30 שניות)
              ← Status OK / Commands
```

### 3. Cart Operations (Real-time)
```
User → Cloud API → MQTT Publish → Raspberry Pi → RS485 → Lock Controller
                                                           ↓
User ← Cloud API ← MQTT Subscribe ← Raspberry Pi ← RS485 ← Status Update
```

### 4. Rental Tracking
```
Cloud DB ← Telemetry ← Raspberry Pi ← RS485 Sensors
```

---

## 🗄️ Database Schema

### Chains (רשתות)
```sql
CREATE TABLE chains (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE
);
```

### Branches (סניפים)
```sql
CREATE TABLE branches (
    id UUID PRIMARY KEY,
    chain_id UUID REFERENCES chains(id),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Devices (רסברי פאי)
```sql
CREATE TABLE devices (
    id UUID PRIMARY KEY,
    branch_id UUID REFERENCES branches(id),
    device_name VARCHAR(100) NOT NULL,
    mac_address VARCHAR(17) UNIQUE NOT NULL,
    serial_number VARCHAR(100),
    device_token TEXT,
    status VARCHAR(50) DEFAULT 'offline',
    last_heartbeat TIMESTAMP,
    firmware_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Controllers (בקרי RS485)
```sql
CREATE TABLE controllers (
    id UUID PRIMARY KEY,
    device_id UUID REFERENCES devices(id),
    controller_address INT NOT NULL,
    port VARCHAR(50),
    baudrate INT DEFAULT 19200,
    status VARCHAR(50) DEFAULT 'inactive'
);
```

### Carts (עגלות)
```sql
CREATE TABLE carts (
    id UUID PRIMARY KEY,
    branch_id UUID REFERENCES branches(id),
    cart_number INT NOT NULL,
    locker_id INT NOT NULL,
    controller_id UUID REFERENCES controllers(id),
    status VARCHAR(50) DEFAULT 'available',
    is_locked BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP,
    maintenance_notes TEXT,
    UNIQUE(branch_id, cart_number)
);
```

### Rentals (השכרות)
```sql
CREATE TABLE rentals (
    id UUID PRIMARY KEY,
    cart_id UUID REFERENCES carts(id),
    branch_id UUID REFERENCES branches(id),
    user_phone VARCHAR(20) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    expected_return TIMESTAMP NOT NULL,
    actual_return TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    duration_minutes INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Telemetry (טלמטריה)
```sql
CREATE TABLE telemetry (
    id SERIAL PRIMARY KEY,
    device_id UUID REFERENCES devices(id),
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## 🔐 Authentication & Security

### Device Authentication
```python
# Device Registration
{
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "serial_number": "RPI-12345",
    "branch_code": "BRANCH-001"
}

# Response
{
    "device_id": "uuid",
    "device_token": "jwt_token",
    "mqtt_config": {
        "broker": "mqtt.cartwise.com",
        "port": 8883,
        "topic": "branch/001/device/uuid"
    }
}
```

### User Authentication
- OTP SMS (existing)
- JWT Tokens (30 days)
- Branch-level permissions

---

## 📡 MQTT Topics Structure

```
cartwise/
├── {chain_id}/
│   └── {branch_id}/
│       ├── devices/
│       │   └── {device_id}/
│       │       ├── status       (device → cloud)
│       │       ├── commands     (cloud → device)
│       │       └── telemetry    (device → cloud)
│       └── carts/
│           └── {cart_id}/
│               ├── lock         (cloud → device)
│               ├── unlock       (cloud → device)
│               └── status       (device → cloud)
```

### Example Topics:
```
# Device Status
cartwise/rami-levi/branch-001/devices/rpi-001/status

# Cart Commands
cartwise/rami-levi/branch-001/carts/cart-001/lock
cartwise/rami-levi/branch-001/carts/cart-001/unlock

# Telemetry
cartwise/rami-levi/branch-001/devices/rpi-001/telemetry
```

---

## 🚀 API Endpoints

### Chain Management
- `GET /api/chains` - List all chains
- `POST /api/chains` - Create chain
- `GET /api/chains/{id}` - Get chain details
- `PUT /api/chains/{id}` - Update chain
- `DELETE /api/chains/{id}` - Delete chain

### Branch Management
- `GET /api/branches` - List branches (filterable by chain)
- `POST /api/branches` - Create branch
- `GET /api/branches/{id}` - Get branch details
- `GET /api/branches/{id}/stats` - Branch statistics

### Device Management
- `POST /api/devices/register` - Register new device
- `POST /api/devices/{id}/heartbeat` - Device heartbeat
- `GET /api/devices/{id}` - Get device info
- `GET /api/devices/{id}/status` - Device status
- `PUT /api/devices/{id}/firmware` - Update firmware

### Cart Management (Multi-Tenant)
- `GET /api/branches/{branch_id}/carts` - List carts in branch
- `POST /api/branches/{branch_id}/carts/assign` - Assign cart
- `POST /api/branches/{branch_id}/carts/return` - Return cart
- `GET /api/branches/{branch_id}/carts/{id}` - Cart details

### Rentals (Multi-Tenant)
- `GET /api/branches/{branch_id}/rentals/active` - Active rentals
- `GET /api/branches/{branch_id}/rentals/history` - Rental history
- `GET /api/branches/{branch_id}/rentals/stats` - Statistics

### Telemetry
- `GET /api/telemetry/devices/{device_id}` - Device telemetry
- `GET /api/telemetry/branches/{branch_id}` - Branch telemetry
- `GET /api/telemetry/chains/{chain_id}` - Chain-wide telemetry

---

## 🔄 Raspberry Pi Client Behavior

### Startup Sequence
1. Load config from `config.json`
2. Connect to Cloud API
3. Authenticate / Register device
4. Connect to MQTT broker
5. Subscribe to command topics
6. Start heartbeat loop
7. Initialize RS485 controller
8. Start main loop

### Main Loop
```python
while True:
    # Send heartbeat (every 30s)
    if time_since_heartbeat > 30:
        send_heartbeat()

    # Check for MQTT commands
    process_mqtt_messages()

    # Poll RS485 status
    check_cart_sensors()

    # Send telemetry
    if time_since_telemetry > 60:
        send_telemetry()

    time.sleep(1)
```

---

## 📊 Dashboard Architecture

### Cloud Dashboard (Admin)
- View all chains
- View all branches
- System-wide analytics
- Device management
- User management

### Branch Dashboard (Manager)
- View branch carts
- View branch rentals
- Real-time status
- Local analytics
- Send commands to devices

### User Interface (Customer)
- Scan QR / Enter phone
- Receive OTP
- Unlock cart
- Return cart
- View history

---

## 🔧 Technology Stack

### Cloud Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 14+
- **MQTT Broker**: Mosquitto / AWS IoT Core
- **Cache**: Redis (for sessions)
- **Queue**: Celery + RabbitMQ (for async tasks)

### Raspberry Pi Client
- **Language**: Python 3.9+
- **MQTT Client**: paho-mqtt
- **Serial**: pyserial
- **HTTP**: requests / aiohttp

### Frontend
- **Admin Dashboard**: React + TypeScript
- **Branch Dashboard**: React + TypeScript
- **User Interface**: HTML + JavaScript (existing)

---

## 📈 Scalability Considerations

### Horizontal Scaling
- FastAPI instances behind load balancer
- PostgreSQL with read replicas
- MQTT broker clustering
- Redis cluster for sessions

### Performance
- Connection pooling (DB)
- Message queuing (MQTT)
- Caching (Redis)
- CDN for static assets

### Monitoring
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Device health monitoring
- Alert system

---

## 🔒 Security Best Practices

1. **Device Security**
   - Unique device tokens
   - Token rotation
   - Certificate-based MQTT (TLS)

2. **API Security**
   - JWT authentication
   - Rate limiting
   - CORS configuration
   - SQL injection prevention

3. **Data Security**
   - Encrypted at rest (DB)
   - Encrypted in transit (HTTPS/TLS)
   - PII data protection
   - GDPR compliance

---

## 🚦 Deployment Strategy

### Development
```
Local PostgreSQL + Mosquitto
```

### Staging
```
AWS RDS + AWS IoT Core
```

### Production
```
AWS RDS Multi-AZ + AWS IoT Core + CloudFront + Load Balancer
```

---

## 📝 Migration Path

### Phase 1: Cloud Backend
1. Create new cloud backend structure
2. Migrate database schema
3. Implement device registration
4. Setup MQTT broker

### Phase 2: Raspberry Pi Client
1. Create client application
2. Test with existing hardware
3. Deploy to one branch (pilot)

### Phase 3: Integration
1. Connect existing frontend
2. Create branch dashboard
3. Full system testing

### Phase 4: Rollout
1. Deploy to production
2. Onboard branches gradually
3. Monitor and optimize

---

**Version:** 2.0.0
**Last Updated:** 2025-10-24
**Status:** Architecture Design Phase
