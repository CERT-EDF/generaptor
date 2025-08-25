"""get-fingerprint command"""

from json import dumps
from pathlib import Path

from ..concept import Collection
from ..helper.logging import get_logger

_LOGGER = get_logger('command.get_fingerprint')


def _print_collection_fingerprint(filepath: Path):
    collection = Collection(filepath=filepath)
    fingerprint = collection.fingerprint
    if not fingerprint:
        _LOGGER.error("failed to retrieve collection fingerprint")
        return
    print(dumps({'filepath': str(filepath), 'fingerprint': fingerprint}))


def _get_fingerprint_cmd(args):
    for filepath in args.collections:
        if filepath.is_file():
            _print_collection_fingerprint(filepath)
            continue
        if filepath.is_dir():
            for item in filepath.glob('Collection_*.zip'):
                _print_collection_fingerprint(item)
            continue
        _LOGGER.warning("skipped %s", filepath)


def setup_cmd(cmd):
    """Setup get-fingerprint command"""
    get_fingerprint = cmd.add_parser(
        'get-fingerprint',
        help="get the collection archive certificate fingerprint",
    )
    get_fingerprint.add_argument(
        'collections',
        metavar='collection',
        nargs='+',
        type=Path,
        help="collection archives",
    )
    get_fingerprint.set_defaults(func=_get_fingerprint_cmd)
