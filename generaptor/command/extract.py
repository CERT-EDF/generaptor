"""extract command"""

from collections.abc import Iterator
from pathlib import Path

from ..concept import Collection, CollectionList, Outcome
from ..helper.crypto import RSAPrivateKey, load_private_key
from ..helper.logging import get_logger

_LOGGER = get_logger('command.extract')


def _check_same_fingerprint(collections: CollectionList, private_key: Path):
    fingerprints = {collection.fingerprint for collection in collections}
    if len(fingerprints) != 1:
        _LOGGER.error("collections shall share the same fingerprint")
        _LOGGER.error("found: %s", fingerprints)
        return False
    fingerprint = fingerprints.pop()
    if not private_key.name.startswith(fingerprint):
        _LOGGER.error("given key does not match given collections fingerprint")
        _LOGGER.error("expected: %s", fingerprint)
        return False
    return True


def _enumerate_collections(args) -> Iterator[Collection]:
    for filepath in args.collections:
        if filepath.is_file():
            yield Collection(filepath=filepath)
            continue
        if filepath.is_dir():
            for item in filepath.glob('Collection_*.zip'):
                yield Collection(filepath=item)
            continue
        _LOGGER.warning("skipped %s", filepath)


def _extract_collection(
    collection: Collection, private_key: RSAPrivateKey, output_directory: Path
):
    try:
        secret = collection.secret(private_key)
    except ValueError:
        _LOGGER.exception("private key does not match collection archive")
        return
    dirname = f'{collection.filepath.stem}'
    directory = output_directory / dirname
    directory.mkdir(parents=True, exist_ok=True)
    _LOGGER.info("extracting: %s", collection.filepath)
    _LOGGER.info("        to: %s", directory)
    outcome = collection.extract_to(directory, secret)
    if outcome == Outcome.PARTIAL:
        _LOGGER.warning("archive partially extracted")


def _extract_cmd(args):
    collections = list(_enumerate_collections(args))
    if not _check_same_fingerprint(collections, args.private_key):
        return
    try:
        private_key = load_private_key(args.private_key)
    except ValueError:
        _LOGGER.exception("invalid private key and/or passphrase")
        return
    if not private_key:
        return
    for collection in collections:
        _extract_collection(collection, private_key, args.output_directory)


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
