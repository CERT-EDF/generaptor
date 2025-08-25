#!/usr/bin/env python3
"""Application"""
from argparse import ArgumentParser

from .__version__ import version
from .command import setup_commands
from .concept import Cache, Config
from .helper.logging import get_logger

_LOGGER = get_logger('main')


def _parse_args():
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
    """Application entry point"""
    _LOGGER.info("Generaptor v%s", version)
    args = _parse_args()
    args.config.directory.mkdir(parents=True, exist_ok=True)
    if not args.cache.directory.is_dir() and args.cmd != 'update':
        _LOGGER.error(
            "cache update is needed, please run 'update' command first"
        )
        return
    args.func(args)


if __name__ == '__main__':
    app()
