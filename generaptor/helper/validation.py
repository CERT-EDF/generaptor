"""Validation helpers"""

from .logging import get_logger

_LOGGER = get_logger('helper.validation')


def check_device(device: str):
    """Check device name"""
    if '"' in device:
        _LOGGER.critical("device name cannot contain '\"'.")
        return False
    return True
