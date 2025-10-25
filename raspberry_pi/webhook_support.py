"""
CartWise Pro - Webhook Support Module
======================================

Sends events to external webhooks (Base44, Zapier, n8n, etc.)
instead of polling APIs constantly.

Author: CartWise Team
Version: 1.0.0
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WebhookManager:
    """
    Manages webhook notifications for cart events.

    Supports:
    - Base44 webhooks
    - Generic HTTP webhooks
    - Multiple webhook URLs
    """

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize webhook manager.

        Args:
            webhook_url: Primary webhook URL (e.g., Base44 function URL)
        """
        self.webhook_url = webhook_url
        self.additional_webhooks = []
        self.enabled = webhook_url is not None

        if self.enabled:
            logger.info(f"Webhook manager initialized: {webhook_url}")
        else:
            logger.info("Webhook manager disabled (no URL provided)")

    def add_webhook(self, url: str, name: str = ""):
        """
        Add an additional webhook URL.

        Args:
            url: Webhook URL
            name: Optional name for logging
        """
        self.additional_webhooks.append({'url': url, 'name': name})
        logger.info(f"Added webhook: {name or url}")

    def send_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        retry: bool = True
    ) -> bool:
        """
        Send event to all configured webhooks.

        Args:
            event_type: Event type (e.g., "cart.assigned", "cart.returned")
            data: Event data
            retry: Retry on failure

        Returns:
            True if at least one webhook succeeded
        """
        if not self.enabled:
            logger.debug(f"Webhooks disabled - skipping event: {event_type}")
            return False

        # Build payload
        payload = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'source': 'cartwise_local_agent'
        }

        success = False

        # Send to primary webhook
        if self.webhook_url:
            if self._send_to_url(self.webhook_url, payload, "Primary", retry):
                success = True

        # Send to additional webhooks
        for webhook in self.additional_webhooks:
            if self._send_to_url(webhook['url'], payload, webhook['name'], retry):
                success = True

        return success

    def _send_to_url(
        self,
        url: str,
        payload: Dict[str, Any],
        name: str = "",
        retry: bool = True
    ) -> bool:
        """
        Send payload to specific webhook URL.

        Args:
            url: Webhook URL
            payload: Event payload
            name: Webhook name for logging
            retry: Retry on failure

        Returns:
            True if successful
        """
        max_retries = 3 if retry else 1

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=5.0,
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code in [200, 201, 204]:
                    logger.info(f"Webhook sent successfully to {name or url}: {payload['event_type']}")
                    return True
                else:
                    logger.warning(
                        f"Webhook {name or url} returned {response.status_code}: {response.text}"
                    )

                    if attempt < max_retries - 1:
                        continue
                    return False

            except requests.exceptions.Timeout:
                logger.error(f"Webhook {name or url} timed out (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    continue
                return False

            except requests.exceptions.RequestException as e:
                logger.error(f"Webhook {name or url} error: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    continue
                return False

            except Exception as e:
                logger.error(f"Unexpected error sending webhook to {name or url}: {e}")
                return False

        return False

    # ========================================================================
    # Convenience methods for common events
    # ========================================================================

    def cart_assigned(
        self,
        cart_id: int,
        user_phone: str,
        rental_id: int,
        locker_id: int,
        start_time: Optional[str] = None
    ):
        """
        Send cart.assigned event.

        Args:
            cart_id: Cart ID
            user_phone: User phone number
            rental_id: Rental record ID
            locker_id: Locker/lock ID
            start_time: Rental start time (ISO format)
        """
        return self.send_event('cart.assigned', {
            'cart_id': cart_id,
            'user_phone': user_phone,
            'rental_id': rental_id,
            'locker_id': locker_id,
            'start_time': start_time or datetime.now().isoformat()
        })

    def cart_returned(
        self,
        cart_id: int,
        user_phone: str,
        rental_id: int,
        locker_id: int,
        end_time: Optional[str] = None
    ):
        """
        Send cart.returned event.

        Args:
            cart_id: Cart ID
            user_phone: User phone number
            rental_id: Rental record ID
            locker_id: Locker/lock ID
            end_time: Return time (ISO format)
        """
        return self.send_event('cart.returned', {
            'cart_id': cart_id,
            'user_phone': user_phone,
            'rental_id': rental_id,
            'locker_id': locker_id,
            'end_time': end_time or datetime.now().isoformat()
        })

    def cart_locked(self, cart_id: int, locker_id: int):
        """Send cart.locked event."""
        return self.send_event('cart.locked', {
            'cart_id': cart_id,
            'locker_id': locker_id,
            'is_locked': True
        })

    def cart_unlocked(self, cart_id: int, locker_id: int):
        """Send cart.unlocked event."""
        return self.send_event('cart.unlocked', {
            'cart_id': cart_id,
            'locker_id': locker_id,
            'is_locked': False
        })

    def cart_overdue(
        self,
        cart_id: int,
        user_phone: str,
        rental_id: int,
        minutes_overdue: int
    ):
        """
        Send cart.overdue event.

        Args:
            cart_id: Cart ID
            user_phone: User phone number
            rental_id: Rental record ID
            minutes_overdue: Minutes past due
        """
        return self.send_event('cart.overdue', {
            'cart_id': cart_id,
            'user_phone': user_phone,
            'rental_id': rental_id,
            'minutes_overdue': minutes_overdue
        })

    def lock_error(
        self,
        cart_id: int,
        locker_id: int,
        error_type: str,
        error_message: str
    ):
        """
        Send lock.error event.

        Args:
            cart_id: Cart ID
            locker_id: Locker ID
            error_type: Error type (e.g., "communication_error", "timeout")
            error_message: Error message
        """
        return self.send_event('lock.error', {
            'cart_id': cart_id,
            'locker_id': locker_id,
            'error_type': error_type,
            'error_message': error_message
        })

    def agent_status(
        self,
        status: str,
        branch_id: str,
        online_carts: int,
        message: str = ""
    ):
        """
        Send agent.status event (heartbeat alternative).

        Args:
            status: Status (e.g., "online", "offline", "error")
            branch_id: Branch ID
            online_carts: Number of carts online
            message: Optional status message
        """
        return self.send_event('agent.status', {
            'status': status,
            'branch_id': branch_id,
            'online_carts': online_carts,
            'message': message
        })


# ============================================================================
# Example usage
# ============================================================================

if __name__ == '__main__':
    # Example: Base44 webhook
    webhook = WebhookManager(
        webhook_url="https://your-app.base44.app/api/functions/cartwiseWebhook"
    )

    # Add additional webhooks (optional)
    webhook.add_webhook(
        url="https://hooks.zapier.com/hooks/catch/xxx/yyy",
        name="Zapier"
    )

    # Send events
    webhook.cart_assigned(
        cart_id=1,
        user_phone="0501234567",
        rental_id=123,
        locker_id=0
    )

    webhook.cart_returned(
        cart_id=1,
        user_phone="0501234567",
        rental_id=123,
        locker_id=0
    )

    webhook.cart_locked(cart_id=1, locker_id=0)
    webhook.cart_unlocked(cart_id=1, locker_id=0)

    print("Webhook examples sent!")
