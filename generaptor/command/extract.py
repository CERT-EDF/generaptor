"""extract command
"""

from pathlib import Path
from ..api import Collection, CollectionList
from ..helper.crypto import load_private_key
from ..helper.logging import LOGGER


def _check_same_fingerprint(collections: CollectionList, private_key: Path):
    fingerprints = {collection.fingerprint for collection in collections}
    if len(fingerprints) != 1:
        LOGGER.error("collections shall share the same fingerprint")
        LOGGER.error("found: %s", fingerprints)
        return False
    fingerprint = fingerprints.pop()
    if not private_key.name.startswith(fingerprint):
        LOGGER.error("given key does not match given collections fingerprint")
        LOGGER.error("expected: %s", fingerprint)
        return False
    return True


def _extract_cmd(args):
    collections = []
    for filepath in args.collections:
        if filepath.is_file():
            collections.append(Collection(filepath=filepath))
            continue
        if filepath.is_dir():
            for item in filepath.glob('Collection_*.zip'):
                collections.append(Collection(filepath=item))
            continue
        LOGGER.warning("skipped %s", filepath)
    if not _check_same_fingerprint(collections, args.private_key):
        return
    try:
        private_key = load_private_key(args.private_key)
    except ValueError:
        LOGGER.exception("invalid private key and/or passphrase")
        return
    if not private_key:
        return
    for collection in collections:
        try:
            secret = collection.secret(private_key)
        except ValueError:
            LOGGER.exception("private key does not match collection archive")
            return
        dirname = f'{collection.filepath.stem}'
        directory = args.output_directory / dirname
        directory.mkdir(parents=True, exist_ok=True)
        LOGGER.info("extracting: %s", collection.filepath)
        LOGGER.info("        to: %s", directory)
        collection.extract_to(directory, secret)


def setup_cmd(cmd):
    """Setup get-fingerprint command"""
    extract = cmd.add_parser(
        'extract',
        help="extract collection archives",
    )
    extract.add_argument(
        '--output-directory',
        '-o',
        type=Path,
        default=Path('extracted'),
        help="set output directory",
    )
    extract.add_argument(
        'private_key',
        type=Path,
        help="private key, given collections must share the same certificate fingerprint",
    )
    extract.add_argument(
        'collections',
        metavar='collection',
        nargs='+',
        type=Path,
        help="collection archives",
    )
    extract.set_defaults(func=_extract_cmd)
