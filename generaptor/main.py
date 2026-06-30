#!/usr/bin/env python3
"""Application entry point module.

This module provides the main application entry point and argument parsing
for the generaptor CLI tool.
"""

from argparse import ArgumentParser
from sys import exit as sys_exit

from .__version__ import version
from .command import setup_commands
from .concept import Cache, Config
from .helper.logging import get_logger

_LOGGER = get_logger('main')


def _parse_args():
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments including command and options.
    """
    parser = ArgumentParser(
        description="Generate Velociraptor-based collectors in no time"
    )
    parser.add_argument(
        '--cache',
        type=Cache.from_string,
        default=Cache(),
        help="Set cache directory",
    )
    parser.add_argument(
        '--config',
        type=Config.from_string,
        default=Config(),
        help="Set config directory",
    )
    cmd = parser.add_subparsers(dest='cmd')
    cmd.required = True
    setup_commands(cmd)
    return parser.parse_args()


def app():
    """Application entry point.

    Main function that initializes the application, checks cache and config
    directories, and executes the selected command.
    """
    _LOGGER.info("Generaptor v%s", version)
    args = _parse_args()
    args.config.directory.mkdir(parents=True, exist_ok=True)
    if not args.cache.directory.is_dir() and args.cmd != 'update':
        _LOGGER.error(
            "cache update is needed, please run 'update' command first"
        )
        sys_exit(1)
    args.func(args)


if __name__ == '__main__':
    app()
