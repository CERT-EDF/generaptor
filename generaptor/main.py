#!/usr/bin/env python3
"""Application
"""
from argparse import ArgumentParser
from .command import setup_commands
from .__version__ import version
from .helper.cache import Cache
from .helper.logging import LOGGER


def _parse_args():
    parser = ArgumentParser(
        description="Generate Velociraptor-based collectors in no time"
    )
    parser.add_argument(
        '--cache',
        type=Cache,
        default=Cache(),
        help="Set cache directory",
    )
    cmd = parser.add_subparsers(dest='cmd')
    cmd.required = True
    setup_commands(cmd)
    return parser.parse_args()


def app():
    """Application entry point"""
    LOGGER.info("Generaptor v%s", version)
    args = _parse_args()
    args.func(args)


if __name__ == '__main__':
    app()
