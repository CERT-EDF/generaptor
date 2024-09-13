"""Validation helpers
"""

from .logging import LOGGER


def check_device(device: str):
    """Check device name"""
    if '"' in device:
        LOGGER.critical("device name cannot contain '\"'.")
        return False
    return True
