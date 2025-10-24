"""
CartWise Pro - Main API Server
================================

FastAPI backend for smart shopping cart management system.

Features:
- User authentication with OTP
- Cart assignment and management
- RS485 lock control
- SMS notifications
- Real-time status updates

Author: CartWise Team
Version: 1.0.0
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("config/.env")

# Import our modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from hardware.rs485 import RS485Controller, LockStatus
from sms.inforu import InforuSMSProvider
from sms.otp import OTPManager
from models.cart import Cart, CartStatus, CartAssignmentRequest, CartReturnRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CartWise Pro API",
    description="Smart Shopping Cart Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# GLOBAL STATE & CONFIGURATION
# ============================================================================

# Load environment variables
INFORU_USERNAME = os.getenv("INFORU_USERNAME", "your_username")
INFORU_PASSWORD = os.getenv("INFORU_PASSWORD", "your_password")
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
BAUD_RATE = int(os.getenv("BAUD_RATE", "9600"))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8001"))

# Initialize components
otp_manager = OTPManager(code_length=4, expiration_minutes=5)
sms_provider = InforuSMSProvider(username=INFORU_USERNAME, password=INFORU_PASSWORD)

# RS485 Controller (will be initialized on startup)
lock_controller: Optional[RS485Controller] = None

# Cart database (in-memory for now - replace with real DB in production)
carts_db: Dict[int, Cart] = {
    1: Cart(cart_id=1, locker_id=1, status=CartStatus.AVAILABLE, is_locked=True),
    2: Cart(cart_id=2, locker_id=2, status=CartStatus.AVAILABLE, is_locked=True),
    3: Cart(cart_id=3, locker_id=3, status=CartStatus.AVAILABLE, is_locked=True),
    4: Cart(cart_id=4, locker_id=4, status=CartStatus.AVAILABLE, is_locked=True),
    5: Cart(cart_id=5, locker_id=5, status=CartStatus.AVAILABLE, is_locked=True),
}

logger.info(f"Initialized {len(carts_db)} carts in database")


# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize hardware connections on startup"""
    global lock_controller

    logger.info("🚀 Starting CartWise Pro API Server...")

    # Initialize RS485 controller
    try:
        lock_controller = RS485Controller(port=SERIAL_PORT, baudrate=BAUD_RATE)
        if lock_controller.connect():
            logger.info("✅ RS485 controller connected")
        else:
            logger.warning("⚠️  RS485 controller not available (running in demo mode)")
            lock_controller = None
    except Exception as e:
        logger.error(f"❌ Failed to initialize RS485 controller: {e}")
        lock_controller = None

    logger.info("✅ CartWise Pro API Server started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down CartWise Pro API Server...")

    if lock_controller:
        lock_controller.disconnect()
        logger.info("RS485 controller disconnected")

    logger.info("✅ Shutdown complete")


# ============================================================================
# API MODELS
# ============================================================================

class OTPRequest(BaseModel):
    """Request OTP for phone number"""
    phone: str


class OTPVerifyRequest(BaseModel):
    """Verify OTP code"""
    phone: str
    otp_code: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    rs485_connected: bool
    sms_configured: bool
    active_carts: int


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_class=FileResponse)
async def root():
    """Serve the main customer interface"""
    static_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "public", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return JSONResponse({"message": "CartWise Pro API - Use /docs for API documentation"})


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns system status and component availability.
    """
    active_carts = sum(1 for cart in carts_db.values() if cart.status == CartStatus.IN_USE)

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        rs485_connected=lock_controller is not None and lock_controller.serial and lock_controller.serial.is_open if lock_controller else False,
        sms_configured=bool(INFORU_USERNAME and INFORU_PASSWORD),
        active_carts=active_carts
    )


@app.get("/carts", response_model=List[Cart])
async def get_carts():
    """
    Get all carts.

    Returns list of all carts with their current status.
    """
    return list(carts_db.values())


@app.get("/carts/available", response_model=List[Cart])
async def get_available_carts():
    """
    Get available carts.

    Returns list of carts that are available for assignment.
    """
    available = [cart for cart in carts_db.values() if cart.status == CartStatus.AVAILABLE]
    return available


@app.get("/carts/{cart_id}", response_model=Cart)
async def get_cart(cart_id: int):
    """
    Get specific cart by ID.

    Args:
        cart_id: Cart identifier

    Returns:
        Cart details
    """
    if cart_id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart not found")

    return carts_db[cart_id]


@app.post("/auth/request-otp")
async def request_otp(request: OTPRequest):
    """
    Request OTP code.

    Generates and sends OTP code via SMS.

    Args:
        request: Phone number to send OTP to

    Returns:
        Success message
    """
    logger.info(f"📱 OTP requested for {request.phone}")

    # Generate OTP
    otp_code = otp_manager.generate_otp(request.phone)

    # Send SMS
    sms_response = sms_provider.send_otp(request.phone, otp_code)

    if not sms_response.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send SMS: {sms_response.error}"
        )

    logger.info(f"✅ OTP sent to {request.phone}")

    return {
        "success": True,
        "message": "קוד אימות נשלח למספר הטלפון שלך",
        "expires_in_minutes": otp_manager.expiration_minutes
    }


@app.post("/auth/verify-otp")
async def verify_otp(request: OTPVerifyRequest):
    """
    Verify OTP code.

    Args:
        request: Phone and OTP code

    Returns:
        Verification result
    """
    logger.info(f"🔍 Verifying OTP for {request.phone}")

    is_valid = otp_manager.validate_otp(request.phone, request.otp_code)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="קוד אימות שגוי או פג תוקף"
        )

    logger.info(f"✅ OTP verified for {request.phone}")

    return {
        "success": True,
        "message": "אימות הצליח",
        "phone": request.phone
    }


@app.post("/carts/assign")
async def assign_cart(request: CartAssignmentRequest):
    """
    Assign an available cart to a user.

    Verifies OTP and assigns the first available cart.

    Args:
        request: Phone and OTP code

    Returns:
        Assigned cart details
    """
    logger.info(f"🛒 Cart assignment requested by {request.phone}")

    # Verify OTP
    is_valid = otp_manager.validate_otp(request.phone, request.otp_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="קוד אימות שגוי או פג תוקף"
        )

    # Find available cart
    available_cart = None
    for cart in carts_db.values():
        if cart.status == CartStatus.AVAILABLE:
            available_cart = cart
            break

    if not available_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="אין עגלות זמינות כרגע"
        )

    # Unlock the cart
    if lock_controller:
        success = lock_controller.unlock_cart(available_cart.locker_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="שגיאה בפתיחת המנעול"
            )
    else:
        logger.warning("⚠️  Running in demo mode - skipping actual unlock")

    # Assign cart
    available_cart.assign(request.phone)

    # Send confirmation SMS
    sms_provider.send_confirmation(request.phone, available_cart.cart_id)

    logger.info(f"✅ Cart {available_cart.cart_id} assigned to {request.phone}")

    return {
        "success": True,
        "message": f"עגלה מספר {available_cart.cart_id} הוקצתה לך בהצלחה",
        "cart": available_cart
    }


@app.post("/carts/{cart_id}/return")
async def return_cart(cart_id: int, request: CartReturnRequest):
    """
    Return a cart.

    Locks the cart and marks it as available.

    Args:
        cart_id: Cart ID to return
        request: User details

    Returns:
        Success message
    """
    logger.info(f"🔄 Cart {cart_id} return requested by {request.phone}")

    if cart_id not in carts_db:
        raise HTTPException(status_code=404, detail="עגלה לא נמצאה")

    cart = carts_db[cart_id]

    # Verify cart is assigned to this user
    if cart.assigned_to != request.phone:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="עגלה זו לא הוקצתה לך"
        )

    # Lock the cart
    if lock_controller:
        success = lock_controller.lock_cart(cart.locker_id)
        if not success:
            logger.warning(f"⚠️  Failed to lock cart {cart_id}, but marking as returned anyway")
    else:
        logger.warning("⚠️  Running in demo mode - skipping actual lock")

    # Mark as returned
    cart.return_cart()
    cart.mark_available()

    logger.info(f"✅ Cart {cart_id} returned and now available")

    return {
        "success": True,
        "message": "תודה! העגלה הוחזרה בהצלחה"
    }


@app.post("/carts/{cart_id}/check-return")
async def check_cart_return(cart_id: int):
    """
    Check if cart was physically returned (micro-switch).

    This endpoint can be called periodically to detect automatic returns.

    Args:
        cart_id: Cart ID to check

    Returns:
        Return status
    """
    if cart_id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart = carts_db[cart_id]

    if lock_controller:
        is_returned = lock_controller.check_cart_returned(cart.locker_id)

        if is_returned and cart.status == CartStatus.IN_USE:
            # Auto-lock and mark as returned
            lock_controller.auto_lock_on_return(cart.locker_id)
            cart.return_cart()
            cart.mark_available()

            logger.info(f"🔄 Cart {cart_id} auto-returned (micro-switch detected)")

            return {
                "returned": True,
                "message": "Cart detected as returned",
                "cart": cart
            }

    return {
        "returned": False,
        "message": "Cart not yet returned"
    }


@app.get("/stats")
async def get_stats():
    """
    Get system statistics.

    Returns:
        System statistics
    """
    total_carts = len(carts_db)
    available = sum(1 for c in carts_db.values() if c.status == CartStatus.AVAILABLE)
    in_use = sum(1 for c in carts_db.values() if c.status == CartStatus.IN_USE)
    maintenance = sum(1 for c in carts_db.values() if c.status == CartStatus.MAINTENANCE)

    return {
        "total_carts": total_carts,
        "available": available,
        "in_use": in_use,
        "maintenance": maintenance,
        "otp_stats": otp_manager.get_stats(),
        "timestamp": datetime.now()
    }


# ============================================================================
# STATIC FILES
# ============================================================================

# Mount static files directory
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "public")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"📁 Static files mounted from {static_dir}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    logger.info(f"🚀 Starting server on {HOST}:{PORT}")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
