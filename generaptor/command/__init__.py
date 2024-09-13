"""Command module
"""

from .update import setup_cmd as setup_update
from .generate import setup_cmd as setup_generate
from .extract import setup_cmd as setup_extract
from .get_globs import setup_cmd as setup_get_globs
from .get_secret import setup_cmd as setup_get_secret
from .get_fingerprint import setup_cmd as setup_get_fingerprint


def setup_commands(cmd):
    """Setup commands"""
    setup_update(cmd)
    setup_generate(cmd)
    setup_extract(cmd)
    setup_get_globs(cmd)
    setup_get_secret(cmd)
    setup_get_fingerprint(cmd)
