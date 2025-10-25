"""
CartWise Pro - Local Agent for Raspberry Pi
============================================

This agent runs on the Raspberry Pi in the store and:
1. Connects to the cloud API
2. Receives unlock/lock commands
3. Controls the RS485 CU16 controller
4. Reports status back to the cloud

Author: CartWise Team
Version: 1.0.0
"""

import sys
import os
import time
import json
import requests
from typing import Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hardware.rs485 import RS485Controller
from core import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


class LocalAgent:
    """
    Local agent that connects Raspberry Pi to cloud API.
    """

    def __init__(
        self,
        cloud_url: str,
        branch_id: str,
        api_key: str,
        serial_port: str = "/dev/ttyUSB0",
        baudrate: int = 19200,
        poll_interval: float = 1.0
    ):
        """
        Initialize local agent.

        Args:
            cloud_url: Cloud API URL (e.g., https://cartwise-cloud.onrender.com)
            branch_id: Unique branch identifier
            api_key: API key for authentication
            serial_port: RS485 serial port
            baudrate: RS485 baud rate
            poll_interval: Polling interval in seconds
        """
        self.cloud_url = cloud_url.rstrip('/')
        self.branch_id = branch_id
        self.api_key = api_key
        self.poll_interval = poll_interval

        # Initialize RS485 controller
        self.controller = RS485Controller(port=serial_port, baudrate=baudrate)

        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

        # State
        self.running = False
        self.last_heartbeat = None

        logger.info(f"Local Agent initialized for branch: {branch_id}")
        logger.info(f"Cloud URL: {cloud_url}")
        logger.info(f"Serial port: {serial_port}")

    def start(self):
        """Start the local agent."""
        logger.info("=" * 60)
        logger.info("Starting CartWise Local Agent")
        logger.info("=" * 60)

        # Connect to RS485 controller
        if not self.controller.connect():
            logger.error("Failed to connect to RS485 controller")
            logger.error("Please check:")
            logger.error("  1. Serial port is correct")
            logger.error("  2. USB adapter is connected")
            logger.error("  3. Permissions are correct (sudo usermod -a -G dialout $USER)")
            return False

        logger.info("RS485 controller connected successfully")

        # Register with cloud
        if not self.register_with_cloud():
            logger.error("Failed to register with cloud")
            return False

        logger.info("Successfully registered with cloud")

        # Start main loop
        self.running = True
        logger.info("Agent is now running - polling for commands...")
        logger.info("=" * 60)

        try:
            while self.running:
                self.main_loop()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            logger.info("\nShutdown requested by user")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.shutdown()

        return True

    def register_with_cloud(self) -> bool:
        """Register this agent with the cloud API."""
        try:
            response = self.session.post(
                f"{self.cloud_url}/api/agent/register",
                json={
                    'branch_id': self.branch_id,
                    'agent_type': 'raspberry_pi',
                    'version': '1.0.0',
                    'capabilities': ['rs485', 'cu16_controller']
                }
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Registered successfully: {data.get('message', 'OK')}")
                return True
            else:
                logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error during registration: {e}")
            return False

    def main_loop(self):
        """Main polling loop - check for commands from cloud."""
        try:
            # Send heartbeat every 30 seconds
            now = datetime.now()
            if self.last_heartbeat is None or (now - self.last_heartbeat).total_seconds() > 30:
                self.send_heartbeat()
                self.last_heartbeat = now

            # Poll for commands
            response = self.session.get(
                f"{self.cloud_url}/api/agent/commands/{self.branch_id}"
            )

            if response.status_code == 200:
                data = response.json()
                commands = data.get('commands', [])

                for command in commands:
                    self.execute_command(command)

            elif response.status_code == 204:
                # No commands - this is normal
                pass

            else:
                logger.warning(f"Unexpected response from cloud: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")

    def send_heartbeat(self):
        """Send heartbeat to cloud."""
        try:
            self.session.post(
                f"{self.cloud_url}/api/agent/heartbeat/{self.branch_id}",
                json={'status': 'online', 'timestamp': datetime.now().isoformat()}
            )
            logger.debug("Heartbeat sent")
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")

    def execute_command(self, command: dict):
        """
        Execute a command from the cloud.

        Args:
            command: Command dictionary with 'type', 'params', etc.
        """
        command_id = command.get('id')
        command_type = command.get('type')
        params = command.get('params', {})

        logger.info(f"Executing command: {command_type} (ID: {command_id})")

        try:
            result = None
            success = False

            if command_type == 'unlock':
                locker_id = params.get('locker_id')
                success = self.controller.unlock_cart(locker_id)
                result = {'locker_id': locker_id, 'unlocked': success}

            elif command_type == 'lock':
                locker_id = params.get('locker_id')
                success = self.controller.lock_cart(locker_id)
                result = {'locker_id': locker_id, 'locked': success}

            elif command_type == 'get_status':
                locker_id = params.get('locker_id')
                state = self.controller.get_lock_state(locker_id)
                if state:
                    success = True
                    result = {
                        'locker_id': locker_id,
                        'locked': state.is_lock_closed(locker_id),
                        'cart_inside': state.has_cart_inside(locker_id)
                    }
                else:
                    result = {'error': 'Failed to get status'}

            elif command_type == 'check_return':
                locker_id = params.get('locker_id')
                returned = self.controller.check_cart_returned(locker_id)
                success = True
                result = {'locker_id': locker_id, 'returned': returned}

            else:
                logger.warning(f"Unknown command type: {command_type}")
                result = {'error': f'Unknown command: {command_type}'}

            # Report result back to cloud
            self.report_command_result(command_id, success, result)

        except Exception as e:
            logger.error(f"Error executing command {command_type}: {e}")
            self.report_command_result(command_id, False, {'error': str(e)})

    def report_command_result(self, command_id: str, success: bool, result: dict):
        """
        Report command execution result back to cloud.

        Args:
            command_id: Command ID
            success: Whether command succeeded
            result: Result data
        """
        try:
            self.session.post(
                f"{self.cloud_url}/api/agent/command-result",
                json={
                    'command_id': command_id,
                    'branch_id': self.branch_id,
                    'success': success,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
            )
            logger.info(f"Command result reported: {command_id} - {'SUCCESS' if success else 'FAILED'}")
        except Exception as e:
            logger.error(f"Failed to report command result: {e}")

    def shutdown(self):
        """Shutdown the agent gracefully."""
        logger.info("Shutting down agent...")
        self.running = False

        # Disconnect RS485
        if self.controller:
            self.controller.disconnect()
            logger.info("RS485 controller disconnected")

        # Notify cloud
        try:
            self.session.post(
                f"{self.cloud_url}/api/agent/disconnect/{self.branch_id}"
            )
            logger.info("Notified cloud of disconnect")
        except:
            pass

        logger.info("Shutdown complete")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='CartWise Local Agent for Raspberry Pi')
    parser.add_argument('--cloud-url', default='https://cartwise-cloud.onrender.com',
                       help='Cloud API URL')
    parser.add_argument('--branch-id', required=True,
                       help='Branch ID (e.g., branch_001)')
    parser.add_argument('--api-key', required=True,
                       help='API key for authentication')
    parser.add_argument('--serial-port', default='/dev/ttyUSB0',
                       help='RS485 serial port (default: /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=19200,
                       help='RS485 baud rate (default: 19200)')
    parser.add_argument('--poll-interval', type=float, default=1.0,
                       help='Polling interval in seconds (default: 1.0)')

    args = parser.parse_args()

    # Create and start agent
    agent = LocalAgent(
        cloud_url=args.cloud_url,
        branch_id=args.branch_id,
        api_key=args.api_key,
        serial_port=args.serial_port,
        baudrate=args.baudrate,
        poll_interval=args.poll_interval
    )

    agent.start()


if __name__ == '__main__':
    main()
