"""
Configuration Module
====================

Centralized configuration management using environment variables.

Author: CartWise Team
Version: 1.0.0
"""

import os
import platform
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from config/.env
load_dotenv("config/.env")


class Settings:
    """Application settings loaded from environment variables."""

    # SMS Configuration (Inforu)
    INFORU_USERNAME: str = os.getenv("INFORU_USERNAME", "your_username")
    INFORU_PASSWORD: str = os.getenv("INFORU_PASSWORD", "your_password")

    # RS485 Serial Port Configuration
    @staticmethod
    def _get_serial_port() -> str:
        """
        Get serial port name based on operating system.

        Automatically converts Windows COM port names to Linux /dev/ paths.

        Windows: COM4 -> COM4
        Linux: COM4 -> /dev/ttyCOM4
        Linux: /dev/ttyUSB0 -> /dev/ttyUSB0 (already correct)
        """
        port = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")

        # If running on Linux and port looks like Windows COM port
        if platform.system() == "Linux":
            # Check if it's a Windows-style COM port (e.g., COM4, COM1)
            if port.upper().startswith("COM") and not port.startswith("/"):
                # Convert COM4 -> /dev/ttyCOM4
                return f"/dev/tty{port}"

        return port

    SERIAL_PORT: str = _get_serial_port.__func__()
    BAUD_RATE: int = int(os.getenv("BAUD_RATE", "9600"))

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))

    # OTP Configuration
    OTP_LENGTH: int = int(os.getenv("OTP_LENGTH", "4"))
    OTP_EXPIRATION_MINUTES: int = int(os.getenv("OTP_EXPIRATION_MINUTES", "5"))
    OTP_MAX_ATTEMPTS: int = int(os.getenv("OTP_MAX_ATTEMPTS", "3"))

    # Database Configuration (Optional - for future use)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", "sqlite:///cartwise.db")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Security Configuration (Optional)
    SECRET_KEY: Optional[str] = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # API Configuration
    API_TITLE: str = "CartWise Pro API"
    API_DESCRIPTION: str = "Smart Shopping Cart Management System"
    API_VERSION: str = "1.0.0"

    # CORS Configuration
    CORS_ORIGINS: list[str] = ["*"]  # In production, specify exact origins


# Create global settings instance
settings = Settings()
