# CartWise Pro Cloud - Extended Hierarchical System
## פרומפט מורחב למערכת היררכית מלאה: Chains → Branches → Stations → Computers

---

## 🎯 GOAL

Create a complete hierarchical multi-tenant cloud system with the following structure:

```
Chain (רשת קמעונאית)
  └── Branch (סניף)
        └── Station (תחנה)
              └── Computer (מחשב/רסברי)
                    └── Cart (עגלה)
                          └── Rental (השכרה)
```

---

## 📊 Database Schema - Extended

### 1. Chains (רשתות)
```sql
CREATE TABLE chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Branches (סניפים)
```sql
CREATE TABLE branches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chain_id UUID REFERENCES chains(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    branch_code VARCHAR(50) NOT NULL UNIQUE,
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(chain_id, branch_code)
);
```

### 3. Stations (תחנות) **NEW**
```sql
CREATE TABLE stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    station_code VARCHAR(50) NOT NULL,
    ip_range VARCHAR(50),
    location_description TEXT,
    num_cart_slots INTEGER DEFAULT 5,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(branch_id, station_code)
);
```

### 4. Computers (מחשבים/רסברי) - Renamed from Devices
```sql
CREATE TABLE computers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    computer_name VARCHAR(100) NOT NULL,
    mac_address VARCHAR(17) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    serial_number VARCHAR(100),
    device_token TEXT,
    status VARCHAR(50) DEFAULT 'offline',
    last_heartbeat TIMESTAMP,
    firmware_version VARCHAR(20),
    hardware_info JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_computers_station ON computers(station_id);
CREATE INDEX idx_computers_status ON computers(status);
CREATE INDEX idx_computers_mac ON computers(mac_address);
```

### 5. Controllers (בקרי RS485)
```sql
CREATE TABLE controllers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    computer_id UUID REFERENCES computers(id) ON DELETE CASCADE,
    controller_address INTEGER NOT NULL,
    port VARCHAR(50),
    baudrate INTEGER DEFAULT 19200,
    status VARCHAR(50) DEFAULT 'inactive',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(computer_id, controller_address)
);
```

### 6. Carts (עגלות)
```sql
CREATE TABLE carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    controller_id UUID REFERENCES controllers(id),
    cart_number INTEGER NOT NULL,
    locker_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'available',
    is_locked BOOLEAN DEFAULT TRUE,
    assigned_to VARCHAR(20),
    last_used TIMESTAMP,
    maintenance_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(station_id, cart_number)
);

CREATE INDEX idx_carts_station ON carts(station_id);
CREATE INDEX idx_carts_status ON carts(status);
```

### 7. Rentals (השכרות)
```sql
CREATE TABLE rentals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID REFERENCES carts(id) ON DELETE CASCADE,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    user_phone VARCHAR(20) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    expected_return TIMESTAMP NOT NULL,
    actual_return TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    duration_minutes INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rentals_station ON rentals(station_id);
CREATE INDEX idx_rentals_user ON rentals(user_phone);
CREATE INDEX idx_rentals_status ON rentals(status);
CREATE INDEX idx_rentals_start ON rentals(start_time);
```

### 8. Telemetry (טלמטריה)
```sql
CREATE TABLE telemetry (
    id SERIAL PRIMARY KEY,
    computer_id UUID REFERENCES computers(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_telemetry_computer ON telemetry(computer_id);
CREATE INDEX idx_telemetry_type ON telemetry(event_type);
CREATE INDEX idx_telemetry_timestamp ON telemetry(timestamp);
```

---

## 🏗️ SQLAlchemy Models

### Chain Model (`models/chain.py`)

```python
"""Chain model - represents a retail chain"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Chain(Base):
    """
    Retail chain (e.g., Rami Levi, Shufersal)

    Attributes:
        id: Unique identifier
        name: Chain name (unique)
        slug: URL-friendly identifier
        contact_email: Contact email
        contact_phone: Contact phone
        description: Chain description
        active: Whether the chain is active
        branches: Related branches
    """
    __tablename__ = "chains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    branches = relationship("Branch", back_populates="chain", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chain {self.name} ({self.slug})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "description": self.description,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "num_branches": len(self.branches) if self.branches else 0
        }
```

### Branch Model (`models/branch.py`)

```python
"""Branch model - represents a store branch"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Branch(Base):
    """
    Store branch within a chain

    Attributes:
        id: Unique identifier
        chain_id: Parent chain ID
        name: Branch name
        branch_code: Unique branch code
        address: Physical address
        city: City
        postal_code: Postal code
        latitude: GPS latitude
        longitude: GPS longitude
        active: Whether the branch is active
    """
    __tablename__ = "branches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chain_id = Column(UUID(as_uuid=True), ForeignKey("chains.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    branch_code = Column(String(50), nullable=False, unique=True, index=True)
    address = Column(Text)
    city = Column(String(100))
    postal_code = Column(String(20))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chain = relationship("Chain", back_populates="branches")
    stations = relationship("Station", back_populates="branch", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Branch {self.name} ({self.branch_code})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "chain_id": str(self.chain_id),
            "name": self.name,
            "branch_code": self.branch_code,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "active": self.active,
            "num_stations": len(self.stations) if self.stations else 0
        }
```

### Station Model (`models/station.py`) **NEW**

```python
"""Station model - represents a cart station within a branch"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Station(Base):
    """
    Cart station within a branch

    A station is a physical location where carts are stored and managed.
    Each station can have multiple computers (Raspberry Pi) controlling the carts.

    Attributes:
        id: Unique identifier
        branch_id: Parent branch ID
        name: Station name
        station_code: Unique station code within branch
        ip_range: IP range for computers in this station
        location_description: Physical location description
        num_cart_slots: Number of cart slots available
        active: Whether the station is active
    """
    __tablename__ = "stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    station_code = Column(String(50), nullable=False, index=True)
    ip_range = Column(String(50))
    location_description = Column(Text)
    num_cart_slots = Column(Integer, default=5)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    branch = relationship("Branch", back_populates="stations")
    computers = relationship("Computer", back_populates="station", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="station", cascade="all, delete-orphan")
    rentals = relationship("Rental", back_populates="station")

    def __repr__(self):
        return f"<Station {self.name} ({self.station_code})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "branch_id": str(self.branch_id),
            "name": self.name,
            "station_code": self.station_code,
            "ip_range": self.ip_range,
            "location_description": self.location_description,
            "num_cart_slots": self.num_cart_slots,
            "active": self.active,
            "num_computers": len(self.computers) if self.computers else 0,
            "num_carts": len(self.carts) if self.carts else 0
        }
```

### Computer Model (`models/computer.py`) - Renamed from Device

```python
"""Computer model - represents a Raspberry Pi or computer controlling carts"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Computer(Base):
    """
    Computer/Raspberry Pi that controls carts in a station

    Attributes:
        id: Unique identifier
        station_id: Parent station ID
        computer_name: Human-readable name
        mac_address: MAC address (unique)
        ip_address: Current IP address
        serial_number: Serial number
        device_token: JWT authentication token
        status: Current status (offline, online, error)
        last_heartbeat: Last heartbeat timestamp
        firmware_version: Firmware version
        hardware_info: Additional hardware info (JSON)
    """
    __tablename__ = "computers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True)
    computer_name = Column(String(100), nullable=False)
    mac_address = Column(String(17), nullable=False, unique=True, index=True)
    ip_address = Column(String(45))
    serial_number = Column(String(100))
    device_token = Column(Text)
    status = Column(String(50), default='offline', index=True)
    last_heartbeat = Column(DateTime)
    firmware_version = Column(String(20))
    hardware_info = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    station = relationship("Station", back_populates="computers")
    controllers = relationship("Controller", back_populates="computer", cascade="all, delete-orphan")
    telemetry = relationship("Telemetry", back_populates="computer")

    def __repr__(self):
        return f"<Computer {self.computer_name} ({self.mac_address})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "station_id": str(self.station_id),
            "computer_name": self.computer_name,
            "mac_address": self.mac_address,
            "ip_address": self.ip_address,
            "serial_number": self.serial_number,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "firmware_version": self.firmware_version,
            "hardware_info": self.hardware_info,
            "num_controllers": len(self.controllers) if self.controllers else 0
        }
```

---

## 🔌 API Endpoints - Extended

### Chains Endpoints (`api/routes/chains.py`)

```python
"""Chain management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from models.chain import Chain
from schemas.chain import ChainCreate, ChainUpdate, ChainResponse

router = APIRouter(prefix="/chains", tags=["chains"])

@router.post("/", response_model=ChainResponse, status_code=status.HTTP_201_CREATED)
async def create_chain(chain_data: ChainCreate, db: Session = Depends(get_db)):
    """
    Create a new retail chain

    Args:
        chain_data: Chain creation data
        db: Database session

    Returns:
        Created chain
    """
    # Check if chain with same name or slug exists
    existing = db.query(Chain).filter(
        (Chain.name == chain_data.name) | (Chain.slug == chain_data.slug)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chain with this name or slug already exists"
        )

    chain = Chain(**chain_data.dict())
    db.add(chain)
    db.commit()
    db.refresh(chain)

    return chain.to_dict()

@router.get("/", response_model=List[ChainResponse])
async def list_chains(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all chains

    Args:
        active_only: Filter only active chains
        db: Database session

    Returns:
        List of chains
    """
    query = db.query(Chain)

    if active_only:
        query = query.filter(Chain.active == True)

    chains = query.order_by(Chain.name).all()
    return [chain.to_dict() for chain in chains]

@router.get("/{chain_id}", response_model=ChainResponse)
async def get_chain(chain_id: UUID, db: Session = Depends(get_db)):
    """
    Get chain by ID

    Args:
        chain_id: Chain ID
        db: Database session

    Returns:
        Chain details
    """
    chain = db.query(Chain).filter(Chain.id == chain_id).first()

    if not chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chain not found"
        )

    return chain.to_dict()

@router.put("/{chain_id}", response_model=ChainResponse)
async def update_chain(
    chain_id: UUID,
    chain_data: ChainUpdate,
    db: Session = Depends(get_db)
):
    """
    Update chain

    Args:
        chain_id: Chain ID
        chain_data: Update data
        db: Database session

    Returns:
        Updated chain
    """
    chain = db.query(Chain).filter(Chain.id == chain_id).first()

    if not chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chain not found"
        )

    for key, value in chain_data.dict(exclude_unset=True).items():
        setattr(chain, key, value)

    db.commit()
    db.refresh(chain)

    return chain.to_dict()

@router.delete("/{chain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chain(chain_id: UUID, db: Session = Depends(get_db)):
    """
    Delete chain (soft delete - set active=False)

    Args:
        chain_id: Chain ID
        db: Database session
    """
    chain = db.query(Chain).filter(Chain.id == chain_id).first()

    if not chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chain not found"
        )

    # Soft delete
    chain.active = False
    db.commit()

    return None
```

### Stations Endpoints (`api/routes/stations.py`) **NEW**

```python
"""Station management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from models.station import Station
from models.branch import Branch
from schemas.station import StationCreate, StationUpdate, StationResponse, StationDetailResponse

router = APIRouter(prefix="/stations", tags=["stations"])

@router.post("/", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
async def create_station(station_data: StationCreate, db: Session = Depends(get_db)):
    """
    Create a new station

    Args:
        station_data: Station creation data
        db: Database session

    Returns:
        Created station
    """
    # Verify branch exists
    branch = db.query(Branch).filter(Branch.id == station_data.branch_id).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )

    # Check if station code exists in this branch
    existing = db.query(Station).filter(
        Station.branch_id == station_data.branch_id,
        Station.station_code == station_data.station_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Station with this code already exists in this branch"
        )

    station = Station(**station_data.dict())
    db.add(station)
    db.commit()
    db.refresh(station)

    return station.to_dict()

@router.get("/", response_model=List[StationResponse])
async def list_stations(
    branch_id: Optional[UUID] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    List stations

    Args:
        branch_id: Filter by branch ID
        active_only: Filter only active stations
        db: Database session

    Returns:
        List of stations
    """
    query = db.query(Station)

    if branch_id:
        query = query.filter(Station.branch_id == branch_id)

    if active_only:
        query = query.filter(Station.active == True)

    stations = query.order_by(Station.name).all()
    return [station.to_dict() for station in stations]

@router.get("/{station_id}", response_model=StationDetailResponse)
async def get_station(station_id: UUID, db: Session = Depends(get_db)):
    """
    Get station details including computers and carts

    Args:
        station_id: Station ID
        db: Database session

    Returns:
        Station details
    """
    station = db.query(Station).filter(Station.id == station_id).first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )

    # Include related data
    result = station.to_dict()
    result["computers"] = [comp.to_dict() for comp in station.computers]
    result["carts"] = [cart.to_dict() for cart in station.carts]

    return result

@router.put("/{station_id}", response_model=StationResponse)
async def update_station(
    station_id: UUID,
    station_data: StationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update station

    Args:
        station_id: Station ID
        station_data: Update data
        db: Database session

    Returns:
        Updated station
    """
    station = db.query(Station).filter(Station.id == station_id).first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )

    for key, value in station_data.dict(exclude_unset=True).items():
        setattr(station, key, value)

    db.commit()
    db.refresh(station)

    return station.to_dict()

@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_station(station_id: UUID, db: Session = Depends(get_db)):
    """
    Delete station (soft delete)

    Args:
        station_id: Station ID
        db: Database session
    """
    station = db.query(Station).filter(Station.id == station_id).first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )

    station.active = False
    db.commit()

    return None
```

---

## 📡 MQTT Topics Structure - Extended

```
cartwise/
└── {chain_slug}/
    └── {branch_code}/
        └── {station_code}/
            └── {computer_id}/
                ├── status          (computer → cloud)
                ├── commands        (cloud → computer)
                ├── telemetry       (computer → cloud)
                └── carts/
                    └── {cart_id}/
                        ├── lock    (cloud → computer)
                        ├── unlock  (cloud → computer)
                        └── status  (computer → cloud)
```

### Example Topics:
```
# Computer Status
cartwise/rami-levi/branch-001/station-A/rpi-001/status

# Cart Commands
cartwise/rami-levi/branch-001/station-A/rpi-001/carts/cart-001/lock
cartwise/rami-levi/branch-001/station-A/rpi-001/carts/cart-001/unlock

# Telemetry
cartwise/rami-levi/branch-001/station-A/rpi-001/telemetry
```

---

## 🔒 Security & Multi-Tenancy

### Tenant Isolation

Every request should include tenant context:
- Chain ID
- Branch ID
- Station ID (optional)

```python
def get_tenant_context(
    chain_id: UUID,
    branch_id: UUID,
    db: Session
):
    """
    Verify tenant context and return validated entities
    """
    chain = db.query(Chain).filter(Chain.id == chain_id).first()
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")

    branch = db.query(Branch).filter(
        Branch.id == branch_id,
        Branch.chain_id == chain_id
    ).first()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found or access denied")

    return {"chain": chain, "branch": branch}
```

---

## ✅ Implementation Checklist

- [ ] Create all database models (Chain, Branch, Station, Computer, Controller, Cart, Rental, Telemetry)
- [ ] Setup database migrations (Alembic)
- [ ] Create Pydantic schemas for all models
- [ ] Implement API endpoints for Chains
- [ ] Implement API endpoints for Branches
- [ ] Implement API endpoints for Stations **NEW**
- [ ] Implement API endpoints for Computers
- [ ] Implement API endpoints for Carts (multi-tenant)
- [ ] Implement API endpoints for Rentals (multi-tenant)
- [ ] Implement MQTT service with new topic structure
- [ ] Implement computer authentication
- [ ] Implement tenant isolation middleware
- [ ] Add comprehensive error handling
- [ ] Add logging throughout
- [ ] Write tests for all endpoints
- [ ] Create API documentation
- [ ] Update Raspberry Pi client for new structure

---

## 🎯 Success Criteria

The system should support:
- ✅ Multiple chains with multiple branches
- ✅ Multiple stations per branch
- ✅ Multiple computers per station
- ✅ Real-time MQTT communication with hierarchical topics
- ✅ Tenant isolation at all levels
- ✅ RESTful API for all CRUD operations
- ✅ Computer registration and authentication
- ✅ Cart management per station
- ✅ Rental tracking per station
- ✅ Telemetry collection per computer

---

**Version:** 2.0.0 Extended
**Last Updated:** 2025-10-24
**Status:** Ready for Implementation
