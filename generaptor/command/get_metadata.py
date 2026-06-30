"""get-metadata command module.

This module provides the CLI command for retrieving metadata from
collection archives.
"""

from pathlib import Path

from ..concept import Collection
from ..helper.json import dump_json
from ..helper.logging import get_logger

_LOGGER = get_logger('command.get_metadata')


def _print_collection_metadata(filepath: Path):
    """Print collection metadata as JSON.

    Args:
        filepath (Path): Path to the collection archive file.
    """
    collection = Collection(filepath=filepath)
    metadata = collection.metadata
    if not metadata:
        _LOGGER.error("failed to retrieve collection metadata")
        return
    print(dump_json({'filepath': str(filepath), 'metadata': metadata}))


def _get_metadata_cmd(args):
    """Handle get-metadata command execution.

    Args:
        args: Parsed command line arguments with collections paths.
    """
    for filepath in args.collections:
        if filepath.is_file():
            _print_collection_metadata(filepath)
            continue
        if filepath.is_dir():
            for item in filepath.glob('Collection_*.zip'):
                _print_collection_metadata(item)
            continue
        _LOGGER.warning("skipped %s", filepath)


def setup_cmd(cmd):
    """Setup get-metadata command.

    Args:
        cmd: argparse subparsers object to add the command to.
    """
    get_metadata = cmd.add_parser(
        'get-metadata',
        help="get the collection archive metadata",
    )
    get_metadata.add_argument(
        'collections',
        metavar='collection',
        nargs='+',
        type=Path,
        help="collection archives",
    )
    get_metadata.set_defaults(func=_get_metadata_cmd)
