"""Command module
"""
from .refresh import setup_refresh
from .generate import setup_generate
from .get_secret import setup_get_secret
from .get_fingerprint import setup_get_fingerprint


def setup_commands(cmd):
    """Setup commands"""
    setup_refresh(cmd)
    setup_generate(cmd)
    setup_get_secret(cmd)
    setup_get_fingerprint(cmd)
