"""
Carts Router
============

Cart management endpoints.

Author: CartWise Team
Version: 1.0.0
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Header

from core import get_logger, settings
from core.constants import HTTPMessages
from models import (
    Cart,
    CartStatus,
    CartAssignmentRequest,
    CartReturnRequest,
    CartReturnInitRequest,
    CartReturnInitResponse,
    Rental,
)
from api.dependencies import (
    get_otp_manager,
    get_sms_provider,
    get_lock_controller,
    get_carts_db,
    get_rental_db,
    get_auth_token_manager,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/carts", tags=["Carts"])

# Default rental duration in minutes (2 hours)
DEFAULT_RENTAL_DURATION = 120


@router.get("", response_model=List[Cart])
async def get_carts(carts_db=Depends(get_carts_db)):
    """Get all carts with their current status."""
    return list(carts_db.values())


@router.get("/available", response_model=List[Cart])
async def get_available_carts(carts_db=Depends(get_carts_db)):
    """Get available carts."""
    available = [cart for cart in carts_db.values() if cart.status == CartStatus.AVAILABLE]
    return available


@router.get("/{cart_id}", response_model=Cart)
async def get_cart(cart_id: int, carts_db=Depends(get_carts_db)):
    """Get specific cart by ID."""
    if cart_id not in carts_db:
        raise HTTPException(status_code=404, detail=HTTPMessages.CART_NOT_FOUND)
    return carts_db[cart_id]


@router.post("/assign")
async def assign_cart(
    request: CartAssignmentRequest,
    otp_manager=Depends(get_otp_manager),
    sms_provider=Depends(get_sms_provider),
    lock_controller=Depends(get_lock_controller),
    carts_db=Depends(get_carts_db),
    rental_db=Depends(get_rental_db),
    auth_token_manager=Depends(get_auth_token_manager),
    authorization: Optional[str] = Header(None),
):
    """
    Assign an available cart to a user.

    Verifies OTP or auth token, assigns cart, and creates rental record.
    """
    logger.info(f"Cart assignment requested by {request.phone}")

    # Check if user has valid auth token (skip OTP verification)
    is_authenticated = False
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        validated_phone = auth_token_manager.validate_token(token)

        if validated_phone == request.phone:
            is_authenticated = True
            logger.info(f"User {request.phone} authenticated via token")

    # If not authenticated via token, verify OTP
    if not is_authenticated:
        is_valid = otp_manager.validate_otp(request.phone, request.otp_code)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=HTTPMessages.INVALID_OTP
            )

    # Check if user already has an active rental
    active_rental = rental_db.get_active_rental_by_phone(request.phone)
    if active_rental:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"יש לך כבר עגלה פעילה (מספר {active_rental.cart_id}). החזר אותה לפני שאתה לוקח עגלה חדשה."
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
            detail=HTTPMessages.NO_CARTS_AVAILABLE,
        )

    # Unlock the cart
    if lock_controller:
        success = lock_controller.unlock_cart(available_cart.locker_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=HTTPMessages.LOCK_ERROR,
            )
    else:
        logger.warning("Running in demo mode - skipping actual unlock")

    # Assign cart
    available_cart.assign(request.phone)

    # Create rental record
    start_time = datetime.now()
    expected_return = start_time + timedelta(minutes=DEFAULT_RENTAL_DURATION)

    rental = Rental(
        cart_id=available_cart.cart_id,
        user_phone=request.phone,
        locker_id=available_cart.locker_id,
        start_time=start_time,
        expected_return=expected_return
    )

    rental_id = rental_db.create_rental(rental)
    logger.info(f"Created rental record {rental_id} for cart {available_cart.cart_id}")

    # Send confirmation SMS with return time
    sms_provider.send_confirmation(request.phone, available_cart.cart_id)

    logger.info(f"Cart {available_cart.cart_id} assigned to {request.phone} (rental {rental_id})")

    return {
        "success": True,
        "message": f"{HTTPMessages.CART_ASSIGNED}. אנא החזר עד {expected_return.strftime('%H:%M')}",
        "cart": available_cart,
        "rental_id": rental_id,
        "expected_return": expected_return.isoformat(),
    }


@router.post("/{cart_id}/return")
async def return_cart(
    cart_id: int,
    request: CartReturnRequest,
    lock_controller=Depends(get_lock_controller),
    carts_db=Depends(get_carts_db),
):
    """Return a cart. Locks the cart and marks it as available."""
    logger.info(f"Cart {cart_id} return requested by {request.phone}")

    if cart_id not in carts_db:
        raise HTTPException(status_code=404, detail=HTTPMessages.CART_NOT_FOUND)

    cart = carts_db[cart_id]

    # Verify cart is assigned to this user
    if cart.assigned_to != request.phone:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=HTTPMessages.CART_NOT_ASSIGNED_TO_USER,
        )

    # Lock the cart
    if lock_controller:
        success = lock_controller.lock_cart(cart.locker_id)
        if not success:
            logger.warning(f"Failed to lock cart {cart_id}, but marking as returned anyway")
    else:
        logger.warning("Running in demo mode - skipping actual lock")

    # Mark as returned
    cart.return_cart()
    cart.mark_available()

    logger.info(f"Cart {cart_id} returned and now available")

    return {"success": True, "message": HTTPMessages.CART_RETURNED}


@router.post("/{cart_id}/check-return")
async def check_cart_return(
    cart_id: int,
    lock_controller=Depends(get_lock_controller),
    carts_db=Depends(get_carts_db),
):
    """Check if cart was physically returned (micro-switch)."""
    if cart_id not in carts_db:
        raise HTTPException(status_code=404, detail=HTTPMessages.CART_NOT_FOUND)

    cart = carts_db[cart_id]

    if lock_controller:
        is_returned = lock_controller.check_cart_returned(cart.locker_id)

        if is_returned and cart.status == CartStatus.IN_USE:
            # Auto-lock and mark as returned
            lock_controller.auto_lock_on_return(cart.locker_id)
            cart.return_cart()
            cart.mark_available()

            logger.info(f"Cart {cart_id} auto-returned (micro-switch detected)")

            return {"returned": True, "message": "Cart detected as returned", "cart": cart}

    return {"returned": False, "message": "Cart not yet returned"}


@router.post("/initiate-return", response_model=CartReturnInitResponse)
async def initiate_cart_return(
    request: CartReturnInitRequest,
    lock_controller=Depends(get_lock_controller),
    carts_db=Depends(get_carts_db),
    rental_db=Depends(get_rental_db),
):
    """
    Initiate cart return process.

    Flow:
    1. User enters phone number
    2. System checks if user has an active cart
    3. System finds the first available (empty) lock
    4. System tells user which lock number to return cart to
    5. User physically returns cart to that lock
    6. Micro-switch detects cart and auto-locks

    Returns:
        Assigned locker number for return
    """
    logger.info(f"Cart return initiated by {request.phone}")

    # Check if user has an active rental (use rental_db as source of truth)
    active_rental = rental_db.get_active_rental_by_phone(request.phone)

    if not active_rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="לא נמצאה עגלה פעילה עבור מספר טלפון זה (No active cart found for this phone number)",
        )

    # Get the cart from carts_db
    user_cart = carts_db.get(active_rental.cart_id)
    if not user_cart:
        logger.error(f"Cart {active_rental.cart_id} not found in carts_db but has active rental!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="שגיאה פנימית - עגלה לא נמצאה (Internal error - cart not found)",
        )

    # Find first available lock using software tracking
    # NOTE: Hardware doesn't support reliable status queries, so we track in software
    available_locker = None
    for i in range(16):
        locker_available = True
        # Check if any cart is currently using this locker
        for cart in carts_db.values():
            if cart.locker_id == i and (cart.status == CartStatus.IN_USE or cart.status == CartStatus.MAINTENANCE):
                locker_available = False
                break
        if locker_available:
            available_locker = i
            logger.info(f"Found available locker (software tracking): {i}")
            break

    if available_locker is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="אין מנעולים פנויים כרגע (No available locks at the moment)",
        )

    logger.info(f"User {request.phone} should return cart to locker {available_locker}")

    return CartReturnInitResponse(
        success=True,
        message=f"אנא החזר את העגלה למנעול מספר {available_locker} (Please return cart to lock #{available_locker})",
        locker_number=available_locker,
        locker_id=available_locker,
    )


@router.post("/complete-return")
async def complete_cart_return(
    request: CartReturnRequest,
    lock_controller=Depends(get_lock_controller),
    carts_db=Depends(get_carts_db),
    rental_db=Depends(get_rental_db),
):
    """
    Complete cart return after physical placement detected.

    This endpoint is called periodically or by user confirmation
    to check if the cart was physically returned to the assigned lock.

    Returns:
        Status of return completion
    """
    logger.info(f"Checking return completion for {request.phone}")

    # Get active rental (source of truth)
    active_rental = rental_db.get_active_rental_by_phone(request.phone)

    if not active_rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="לא נמצאה עגלה פעילה (No active cart found)",
        )

    # Get cart from carts_db
    user_cart = carts_db.get(active_rental.cart_id)
    if not user_cart:
        logger.error(f"Cart {active_rental.cart_id} not found in carts_db but has active rental!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="שגיאה פנימית - עגלה לא נמצאה (Internal error - cart not found)",
        )

    # Check if cart was returned using lock controller
    if lock_controller:
        is_returned = lock_controller.check_cart_returned(user_cart.locker_id)

        if is_returned:
            # Cart detected - complete return process
            user_cart.return_cart()
            user_cart.mark_available()

            # CRITICAL: Update rental in database
            active_rental.mark_returned()
            rental_db.update_rental(active_rental)

            logger.info(f"Cart return completed successfully for {request.phone} (rental {active_rental.rental_id})")

            return {
                "success": True,
                "message": "העגלה הוחזרה בהצלחה! (Cart returned successfully!)",
                "returned": True,
            }
        else:
            return {
                "success": False,
                "message": "העגלה עדיין לא זוהתה במנעול (Cart not yet detected in lock)",
                "returned": False,
            }
    else:
        # Demo mode - auto-complete
        logger.warning("Demo mode: auto-completing return")
        user_cart.return_cart()
        user_cart.mark_available()

        # CRITICAL: Update rental in database
        active_rental.mark_returned()
        rental_db.update_rental(active_rental)

        logger.info(f"Cart return completed in demo mode for {request.phone} (rental {active_rental.rental_id})")

        return {
            "success": True,
            "message": "העגלה הוחזרה בהצלחה (Demo mode)",
            "returned": True,
        }
