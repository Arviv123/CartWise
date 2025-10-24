"""
Logging System Demo
===================

Demonstrates the new logging system with dual output (console + file).

This file shows examples of:
- INFO level logging for normal operations
- ERROR level logging for failures
- DEBUG level logging for detailed traces
- Function entry/exit logging

Author: CartWise Team
Version: 1.0.0
"""

from core import setup_logging, get_logger, log_function_call, log_function_exit

# Initialize logging system (console + file)
setup_logging(level="DEBUG")  # Use DEBUG to see all log levels

# Get logger for this module
logger = get_logger(__name__)


def process_cart_assignment(user_phone: str, cart_id: int) -> dict:
    """
    Demo function that shows logging in action.

    Args:
        user_phone: User's phone number
        cart_id: Cart identifier

    Returns:
        Result dictionary
    """
    # Log function entry with parameters
    log_function_call(logger, "process_cart_assignment", user_phone=user_phone, cart_id=cart_id)

    try:
        # INFO: Normal operation logging
        logger.info(f"Starting cart assignment for user {user_phone}")
        logger.info(f"Selected cart ID: {cart_id}")

        # DEBUG: Detailed trace logging
        logger.debug(f"Validating user phone: {user_phone}")
        logger.debug(f"Checking cart availability: {cart_id}")

        # Simulate some validation
        if not user_phone.startswith("05"):
            # ERROR: Log validation failure
            logger.error(f"Invalid phone number format: {user_phone}")
            result = {"success": False, "error": "Invalid phone number"}
            log_function_exit(logger, "process_cart_assignment", result=result)
            return result

        if cart_id > 100:
            # WARNING: Log suspicious cart ID
            logger.warning(f"Cart ID {cart_id} is unusually high")

        # INFO: Success
        logger.info(f"Cart {cart_id} successfully assigned to {user_phone}")

        result = {"success": True, "cart_id": cart_id, "user": user_phone}
        log_function_exit(logger, "process_cart_assignment", result=result)
        return result

    except Exception as e:
        # ERROR: Log exception with traceback
        logger.error(f"Failed to process cart assignment: {e}", exc_info=True)
        result = {"success": False, "error": str(e)}
        log_function_exit(logger, "process_cart_assignment", result=result)
        return result


def demo_all_log_levels():
    """Demonstrate all logging levels."""
    logger.info("=" * 80)
    logger.info("LOGGING LEVELS DEMO")
    logger.info("=" * 80)

    # DEBUG - Detailed diagnostic information
    logger.debug("This is a DEBUG message - detailed diagnostic info")

    # INFO - General informational messages
    logger.info("This is an INFO message - normal operation")

    # WARNING - Warning messages for potentially harmful situations
    logger.warning("This is a WARNING message - something unusual happened")

    # ERROR - Error messages for serious problems
    logger.error("This is an ERROR message - operation failed")

    # CRITICAL - Critical messages for very serious errors
    logger.critical("This is a CRITICAL message - system might be unstable")

    logger.info("=" * 80)


def demo_real_world_scenario():
    """Demonstrate real-world usage scenarios."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("REAL-WORLD SCENARIO DEMO")
    logger.info("=" * 80)

    # Scenario 1: Successful cart assignment
    logger.info("\n--- Scenario 1: Successful Assignment ---")
    result1 = process_cart_assignment("0501234567", 5)
    logger.info(f"Result: {result1}")

    # Scenario 2: Invalid phone number
    logger.info("\n--- Scenario 2: Invalid Phone Number ---")
    result2 = process_cart_assignment("123456", 3)
    logger.info(f"Result: {result2}")

    # Scenario 3: High cart ID (warning)
    logger.info("\n--- Scenario 3: High Cart ID ---")
    result3 = process_cart_assignment("0509876543", 150)
    logger.info(f"Result: {result3}")

    logger.info("=" * 80)


if __name__ == "__main__":
    logger.info("Starting Logging System Demo...")
    logger.info("Logs are being written to BOTH console and file (logs/cartwise.log)")
    logger.info("")

    # Run demos
    demo_all_log_levels()
    demo_real_world_scenario()

    logger.info("")
    logger.info("Demo completed! Check logs/cartwise.log to see the file output.")
    logger.info("=" * 80)
