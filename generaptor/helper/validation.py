"""Validation helpers module.

This module provides input validation functionality for generaptor.
"""

from .logging import get_logger

_LOGGER = get_logger('helper.validation')


def check_device(device: str):
    """Check device name.

    Validates that a device name does not contain problematic characters.

    Args:
        device (str): Device name to validate.

    Returns:
        bool: True if device name is valid, False if it contains invalid characters.
    """
    if '"' in device:
        _LOGGER.critical("device name cannot contain '\"'.")
        return False
    return True
