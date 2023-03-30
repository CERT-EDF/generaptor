"""get-fingerprint command
"""
from pathlib import Path
from ..helper.logging import LOGGER
from ..helper.collection import collection_metadata


def _print_collection_fingerprint(collection: Path):
    metadata = collection_metadata(collection)
    if not metadata:
        LOGGER.error("failed to retrieve metadata from collection.")
        return
    if 'fingerprint_hex' not in metadata:
        LOGGER.error("metadata field not found: fingerprint_hex")
        return
    fingerprint_hex = metadata['fingerprint_hex']
    print(f"{fingerprint_hex}:{collection}")


def _get_fingerprint_cmd(args):
    for collection in args.collections:
        if collection.is_file():
            _print_collection_fingerprint(collection)
            continue
        if collection.is_dir():
            for item in collection.glob('Collection_*.zip'):
                _print_collection_fingerprint(item)
            continue
        LOGGER.warning("skipped %s", collection)


def setup_get_fingerprint(cmd):
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
