"""Generaptor Logging Helper module.

This module configures and provides logging utilities for the generaptor application,
using Rich console formatting for enhanced log output.
"""

from logging import basicConfig, getLogger
from os import getenv

from rich.console import Console
from rich.logging import RichHandler

DEBUG = int(getenv('GENERAPTOR_DEBUG', '0'))

# Setup logging facility
basicConfig(
    level='DEBUG' if DEBUG else 'INFO',
    format="(%(name)s): %(message)s",
    datefmt="[%Y-%m-%dT%H:%M:%S]",
    handlers=[RichHandler(console=Console(stderr=True), show_path=False)],
)


def get_logger(name: str, root: str = 'generaptor'):
    """Retrieve logger for given name.

    Args:
        name (str): Logger name (will be prefixed with root).
        root (str): Root logger name prefix. Defaults to 'generaptor'.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return getLogger('.'.join([root, name]))
