"""get-metadata command"""

from json import dumps
from pathlib import Path

from ..concept import Collection
from ..helper.logging import get_logger

_LOGGER = get_logger('command.get_metadata')


def _print_collection_metadata(filepath: Path):
    collection = Collection(filepath=filepath)
    metadata = collection.metadata
    if not metadata:
        _LOGGER.error("failed to retrieve collection metadata")
        return
    print(dumps({'filepath': str(filepath), 'metadata': metadata}))


def _get_metadata_cmd(args):
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
    """Setup get-metadata command"""
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
