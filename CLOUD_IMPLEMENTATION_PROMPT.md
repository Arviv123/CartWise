# CartWise Pro Cloud - Complete Implementation Prompt
## פרומפט מלא ליצירת מערכת ענן רב-סניפית

---

## 🎯 GOAL

Create a complete multi-tenant cloud system for CartWise Pro that supports:
- Multiple retail chains (Chains)
- Multiple branches per chain
- Multiple Raspberry Pi devices per branch
- RS485 communication with lock controllers
- Real-time MQTT communication
- Cloud dashboard for monitoring
- Device authentication and management

---

## 📋 EXISTING CODEBASE

The existing CartWise Pro system is a single-branch system located at:
```
C:\Users\חיים\CartWise-Pro\
```

**Current Structure:**
```
CartWise-Pro/
├── src/
│   ├── api/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── carts.py
│   │   │   └── rentals.py
│   │   ├── dependencies.py
│   │   └── main.py
│   ├── database/
│   │   ├── carts_db.py
│   │   └── rental_db.py
│   ├── hardware/
│   │   └── rs485.py
│   ├── models/
│   │   ├── cart.py
│   │   ├── rental.py
│   │   └── requests.py
│   ├── services/
│   │   ├── otp_manager.py
│   │   └── sms_provider.py
│   └── utils/
│       ├── auth_tokens.py
│       ├── http_messages.py
│       └── logger.py
├── public/
│   └── index.html
├── data/
│   └── rentals.db
├── requirements.txt
├── run_server.py
└── Dockerfile
```

**Current Features:**
- OTP authentication via SMS
- Cart assignment and return
- Rental tracking with SQLite
- RS485 communication (KERONG CU16 protocol)
- Token-based authentication (30 days)
- Demo mode (works without hardware)

---

## 🏗️ NEW ARCHITECTURE TO BUILD

Create a **new parallel structure** called `cartwise-cloud/` that will coexist with the current system:

```
CartWise-Pro/                    # Existing system (keep as-is)
│
cartwise-cloud/                  # NEW CLOUD SYSTEM
├── backend/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── logging_config.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chain.py
│   │   ├── branch.py
│   │   ├── device.py
│   │   ├── controller.py
│   │   ├── cart.py
│   │   ├── rental.py
│   │   ├── telemetry.py
│   │   └── user.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chains.py
│   │   │   ├── branches.py
│   │   │   ├── devices.py
│   │   │   ├── carts.py
│   │   │   ├── rentals.py
│   │   │   └── telemetry.py
│   │   └── main.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── mqtt_service.py
│   │   ├── device_auth.py
│   │   ├── sync_service.py
│   │   └── telemetry_service.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chain.py
│   │   ├── branch.py
│   │   ├── device.py
│   │   ├── cart.py
│   │   └── rental.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_chains.py
│   │   ├── test_branches.py
│   │   ├── test_devices.py
│   │   └── test_mqtt.py
│   │
│   ├── migrations/
│   │   └── versions/
│   │
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── main.py
│
├── raspberry-client/
│   ├── main.py
│   ├── config.py
│   ├── cloud_sync.py
│   ├── mqtt_listener.py
│   ├── rs485_driver.py
│   ├── telemetry.py
│   ├── logger.py
│   ├── config.example.json
│   ├── requirements.txt
│   └── install.sh
│
├── dashboard/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chains/
│   │   │   ├── branches/
│   │   │   ├── devices/
│   │   │   └── monitoring/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   ├── API.md
│   ├── MQTT.md
│   ├── DEVICE_SETUP.md
│   └── DEPLOYMENT.md
│
└── README.md
```

---

## 🗄️ DATABASE MODELS (SQLAlchemy)

### 1. Chain Model (`models/chain.py`)

```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Chain(Base):
    """
    Represents a retail chain (e.g., Rami Levi, Shufersal)
    """
    __tablename__ = "chains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    branches = relationship("Branch", back_populates="chain", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chain {self.name}>"
```

### 2. Branch Model (`models/branch.py`)

```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Branch(Base):
    """
    Represents a branch/store within a chain
    """
    __tablename__ = "branches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chain_id = Column(UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False)
    name = Column(String(255), nullable=False)
    branch_code = Column(String(50), unique=True, nullable=False, index=True)
    address = Column(String)
    city = Column(String(100))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chain = relationship("Chain", back_populates="branches")
    devices = relationship("Device", back_populates="branch", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="branch", cascade="all, delete-orphan")
    rentals = relationship("Rental", back_populates="branch")

    def __repr__(self):
        return f"<Branch {self.name} ({self.branch_code})>"
```

### 3. Device Model (`models/device.py`)

```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Device(Base):
    """
    Represents a Raspberry Pi device in a branch
    """
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    device_name = Column(String(100), nullable=False)
    mac_address = Column(String(17), unique=True, nullable=False, index=True)
    serial_number = Column(String(100))
    device_token = Column(String)  # JWT token for device auth
    status = Column(String(50), default='offline')  # offline, online, error
    last_heartbeat = Column(DateTime)
    firmware_version = Column(String(20))
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    branch = relationship("Branch", back_populates="devices")
    controllers = relationship("Controller", back_populates="device", cascade="all, delete-orphan")
    telemetry = relationship("Telemetry", back_populates="device")

    def __repr__(self):
        return f"<Device {self.device_name} ({self.mac_address})>"
```

### 4. Controller Model (`models/controller.py`)

```python
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Controller(Base):
    """
    Represents an RS485 controller connected to a device
    """
    __tablename__ = "controllers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    controller_address = Column(Integer, nullable=False)
    port = Column(String(50))  # e.g., /dev/ttyUSB0
    baudrate = Column(Integer, default=19200)
    status = Column(String(50), default='inactive')  # inactive, active, error
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    device = relationship("Device", back_populates="controllers")
    carts = relationship("Cart", back_populates="controller")

    def __repr__(self):
        return f"<Controller {self.controller_address} on {self.port}>"
```

### 5. Cart Model (Multi-tenant) (`models/cart.py`)

```python
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Cart(Base):
    """
    Represents a shopping cart in a branch
    """
    __tablename__ = "carts"
    __table_args__ = (
        UniqueConstraint('branch_id', 'cart_number', name='unique_branch_cart'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    controller_id = Column(UUID(as_uuid=True), ForeignKey("controllers.id"))
    cart_number = Column(Integer, nullable=False)
    locker_id = Column(Integer, nullable=False)
    status = Column(String(50), default='available')  # available, in_use, maintenance
    is_locked = Column(Boolean, default=True)
    assigned_to = Column(String(20))  # phone number
    last_used = Column(DateTime)
    maintenance_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    branch = relationship("Branch", back_populates="carts")
    controller = relationship("Controller", back_populates="carts")
    rentals = relationship("Rental", back_populates="cart")

    def __repr__(self):
        return f"<Cart {self.cart_number} in {self.branch.name}>"
```

### 6. Rental Model (Multi-tenant) (`models/rental.py`)

```python
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Rental(Base):
    """
    Represents a cart rental
    """
    __tablename__ = "rentals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    user_phone = Column(String(20), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    expected_return = Column(DateTime, nullable=False)
    actual_return = Column(DateTime)
    status = Column(String(50), default='active')  # active, returned, returned_late, overdue
    duration_minutes = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cart = relationship("Cart", back_populates="rentals")
    branch = relationship("Branch", back_populates="rentals")

    def __repr__(self):
        return f"<Rental {self.id} - Cart {self.cart_id}>"
```

### 7. Telemetry Model (`models/telemetry.py`)

```python
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base

class Telemetry(Base):
    """
    Stores telemetry data from devices
    """
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    device = relationship("Device", back_populates="telemetry")

    def __repr__(self):
        return f"<Telemetry {self.event_type} from {self.device_id}>"
```

---

## 🔌 CORE CONFIGURATION

### `core/config.py`

```python
"""
Core configuration for CartWise Cloud
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App
    APP_NAME: str = "CartWise Cloud"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api"

    # MQTT
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_USE_TLS: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30
    DEVICE_TOKEN_EXPIRE_DAYS: int = 365

    # SMS (Inforu)
    INFORU_USERNAME: Optional[str] = None
    INFORU_PASSWORD: Optional[str] = None

    # Telemetry
    TELEMETRY_RETENTION_DAYS: int = 90

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### `core/database.py`

```python
"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency for getting database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 📡 MQTT SERVICE

### `services/mqtt_service.py`

```python
"""
MQTT Service for real-time communication with devices
"""
import paho.mqtt.client as mqtt
import json
import logging
from typing import Callable, Dict, Any
from core.config import settings

logger = logging.getLogger(__name__)

class MQTTService:
    """
    MQTT service for device communication
    """

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.message_handlers: Dict[str, Callable] = {}

        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        if settings.MQTT_USE_TLS:
            self.client.tls_set()

    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            self.client.loop_start()
            logger.info(f"Connected to MQTT broker at {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            logger.info("Successfully connected to MQTT broker")
            # Subscribe to all device status topics
            self.client.subscribe("cartwise/+/+/devices/+/status")
            self.client.subscribe("cartwise/+/+/carts/+/status")
            self.client.subscribe("cartwise/+/+/devices/+/telemetry")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")

    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode())
            logger.debug(f"Received message on {topic}: {payload}")

            # Call registered handlers
            for pattern, handler in self.message_handlers.items():
                if pattern in topic:
                    handler(topic, payload)
        except Exception as e:
            logger.error(f"Error processing message on {topic}: {e}")

    def register_handler(self, topic_pattern: str, handler: Callable):
        """Register a message handler for a topic pattern"""
        self.message_handlers[topic_pattern] = handler
        logger.info(f"Registered handler for topic pattern: {topic_pattern}")

    def publish(self, topic: str, payload: Dict[str, Any]):
        """Publish a message to a topic"""
        try:
            payload_str = json.dumps(payload)
            result = self.client.publish(topic, payload_str, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic}: {payload}")
            else:
                logger.error(f"Failed to publish to {topic}")
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")

    def send_command_to_device(self, chain_slug: str, branch_code: str, device_id: str, command: Dict[str, Any]):
        """Send a command to a device"""
        topic = f"cartwise/{chain_slug}/{branch_code}/devices/{device_id}/commands"
        self.publish(topic, command)

    def send_cart_command(self, chain_slug: str, branch_code: str, cart_id: str, command: str):
        """Send a command to a cart (lock/unlock)"""
        topic = f"cartwise/{chain_slug}/{branch_code}/carts/{cart_id}/{command}"
        self.publish(topic, {"timestamp": datetime.utcnow().isoformat()})

# Global MQTT service instance
mqtt_service = MQTTService()
```

---

## 🔐 DEVICE AUTHENTICATION

### `services/device_auth.py`

```python
"""
Device authentication and token management
"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def create_device_token(device_id: str, mac_address: str) -> str:
    """
    Create JWT token for device authentication
    """
    expire = datetime.utcnow() + timedelta(days=settings.DEVICE_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": device_id,
        "mac": mac_address,
        "type": "device",
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_device_token(token: str) -> dict:
    """
    Verify device token and return payload
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "device":
            raise ValueError("Invalid token type")
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        raise ValueError("Invalid token")
```

---

## 🚀 API ENDPOINTS

### `api/routes/devices.py`

```python
"""
Device management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime
from core.database import get_db
from models.device import Device
from models.branch import Branch
from services.device_auth import create_device_token, verify_device_token
from schemas.device import DeviceRegister, DeviceResponse, HeartbeatRequest

router = APIRouter(prefix="/devices", tags=["devices"])

@router.post("/register", response_model=DeviceResponse)
async def register_device(
    request: DeviceRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new device
    """
    # Check if branch exists
    branch = db.query(Branch).filter(Branch.branch_code == request.branch_code).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # Check if device already exists
    existing_device = db.query(Device).filter(Device.mac_address == request.mac_address).first()
    if existing_device:
        # Update existing device
        device = existing_device
        device.device_name = request.device_name
        device.serial_number = request.serial_number
        device.firmware_version = request.firmware_version
    else:
        # Create new device
        device = Device(
            branch_id=branch.id,
            device_name=request.device_name,
            mac_address=request.mac_address,
            serial_number=request.serial_number,
            firmware_version=request.firmware_version,
            status='online'
        )
        db.add(device)

    # Generate device token
    device_token = create_device_token(str(device.id), device.mac_address)
    device.device_token = device_token
    device.last_heartbeat = datetime.utcnow()

    db.commit()
    db.refresh(device)

    return {
        "device_id": str(device.id),
        "device_token": device_token,
        "mqtt_config": {
            "broker": settings.MQTT_BROKER,
            "port": settings.MQTT_PORT,
            "topic": f"cartwise/{branch.chain.slug}/{branch.branch_code}/devices/{device.id}"
        }
    }

@router.post("/{device_id}/heartbeat")
async def device_heartbeat(
    device_id: str,
    request: HeartbeatRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Device heartbeat endpoint
    """
    # Verify device token
    token = authorization.replace("Bearer ", "")
    try:
        payload = verify_device_token(token)
        if payload["sub"] != device_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Update device
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.last_heartbeat = datetime.utcnow()
    device.status = request.status
    device.ip_address = request.ip_address

    db.commit()

    return {"status": "ok", "message": "Heartbeat received"}
```

---

## 🖥️ RASPBERRY PI CLIENT

### `raspberry-client/main.py`

```python
"""
CartWise Raspberry Pi Client
Main entry point
"""
import time
import logging
from config import Config
from cloud_sync import CloudSync
from mqtt_listener import MQTTListener
from rs485_driver import RS485Driver
from telemetry import TelemetryCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main loop"""
    logger.info("Starting CartWise Raspberry Pi Client")

    # Load configuration
    config = Config.load()

    # Initialize components
    cloud_sync = CloudSync(config)
    mqtt_listener = MQTTListener(config)
    rs485_driver = RS485Driver(config)
    telemetry = TelemetryCollector(config)

    # Register device with cloud
    logger.info("Registering device with cloud...")
    device_info = cloud_sync.register()
    logger.info(f"Device registered: {device_info['device_id']}")

    # Connect MQTT
    logger.info("Connecting to MQTT broker...")
    mqtt_listener.connect(device_info)

    # Initialize RS485
    logger.info("Initializing RS485 controller...")
    rs485_driver.initialize()

    # Main loop
    heartbeat_interval = 30
    telemetry_interval = 60
    last_heartbeat = 0
    last_telemetry = 0

    try:
        while True:
            current_time = time.time()

            # Send heartbeat
            if current_time - last_heartbeat >= heartbeat_interval:
                cloud_sync.send_heartbeat()
                last_heartbeat = current_time

            # Send telemetry
            if current_time - last_telemetry >= telemetry_interval:
                telemetry_data = telemetry.collect()
                cloud_sync.send_telemetry(telemetry_data)
                last_telemetry = current_time

            # Process MQTT messages
            mqtt_listener.process_messages()

            # Check RS485 sensors
            rs485_driver.check_sensors()

            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        mqtt_listener.disconnect()
        rs485_driver.close()

if __name__ == "__main__":
    main()
```

### `raspberry-client/cloud_sync.py`

```python
"""
Cloud synchronization for Raspberry Pi client
"""
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CloudSync:
    """
    Handles communication with cloud API
    """

    def __init__(self, config):
        self.config = config
        self.api_url = config.get('cloud_api_url')
        self.device_token = None
        self.device_id = None

    def register(self) -> Dict[str, Any]:
        """
        Register device with cloud
        """
        url = f"{self.api_url}/devices/register"
        data = {
            "device_name": self.config.get('device_name'),
            "mac_address": self.config.get('mac_address'),
            "serial_number": self.config.get('serial_number'),
            "branch_code": self.config.get('branch_code'),
            "firmware_version": "1.0.0"
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            self.device_token = result['device_token']
            self.device_id = result['device_id']

            logger.info(f"Device registered successfully: {self.device_id}")
            return result

        except requests.RequestException as e:
            logger.error(f"Failed to register device: {e}")
            raise

    def send_heartbeat(self):
        """
        Send heartbeat to cloud
        """
        if not self.device_token or not self.device_id:
            logger.error("Device not registered")
            return

        url = f"{self.api_url}/devices/{self.device_id}/heartbeat"
        headers = {"Authorization": f"Bearer {self.device_token}"}
        data = {
            "status": "online",
            "ip_address": self._get_ip_address()
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            logger.debug("Heartbeat sent successfully")
        except requests.RequestException as e:
            logger.error(f"Failed to send heartbeat: {e}")

    def send_telemetry(self, telemetry_data: Dict[str, Any]):
        """
        Send telemetry data to cloud
        """
        # Implementation
        pass

    def _get_ip_address(self) -> str:
        """Get local IP address"""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "unknown"
```

---

## 📝 REQUIREMENTS

### `backend/requirements.txt`

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
paho-mqtt==1.6.1
redis==5.0.1
celery==5.3.4
pytest==7.4.3
requests==2.31.0
python-dotenv==1.0.0
```

### `raspberry-client/requirements.txt`

```
requests==2.31.0
paho-mqtt==1.6.1
pyserial==3.5
python-dotenv==1.0.0
```

---

## 🎯 IMPLEMENTATION INSTRUCTIONS

### FOR CLAUDE/GPT:

**Please create the complete codebase following this prompt:**

1. **Create the folder structure exactly as specified**

2. **Implement all database models** with proper relationships and constraints

3. **Implement core services**:
   - MQTT service with pub/sub
   - Device authentication
   - Cloud sync service
   - Telemetry collection

4. **Create API endpoints** for:
   - Chain management (CRUD)
   - Branch management (CRUD)
   - Device registration and management
   - Multi-tenant cart operations
   - Multi-tenant rental tracking
   - Telemetry retrieval

5. **Build Raspberry Pi client** that:
   - Registers with cloud
   - Sends heartbeats
   - Listens to MQTT commands
   - Controls RS485 (integrate existing code)
   - Sends telemetry

6. **Create configuration files**:
   - `.env.example` for backend
   - `config.example.json` for Raspberry client
   - Docker files
   - Database migration scripts (Alembic)

7. **Add comprehensive documentation**:
   - API documentation
   - MQTT topic structure
   - Device setup guide
   - Deployment guide

8. **Include tests** for critical components

9. **Add error handling and logging** throughout

10. **Ensure security best practices**:
    - JWT tokens
    - Input validation
    - SQL injection prevention
    - Rate limiting

---

## ✅ SUCCESS CRITERIA

The system should support:
- ✅ Multiple chains with multiple branches
- ✅ Device registration and authentication
- ✅ Real-time MQTT communication
- ✅ Multi-tenant cart and rental operations
- ✅ Telemetry collection and storage
- ✅ REST API for all operations
- ✅ Raspberry Pi client that works standalone
- ✅ Database migrations
- ✅ Comprehensive error handling
- ✅ Logging and monitoring

---

**Version:** 2.0.0
**Last Updated:** 2025-10-24
**Estimated Time:** This is a large project - expect 2-3 hours for complete implementation
