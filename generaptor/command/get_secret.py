"""get-secret command"""

from json import dumps
from pathlib import Path

from ..concept import Collection
from ..helper.crypto import RSAPrivateKey, load_private_key
from ..helper.logging import get_logger

_LOGGER = get_logger('command.get_secret')


def _print_collection_secret(private_key: RSAPrivateKey, filepath: Path):
    collection = Collection(filepath=filepath)
    _LOGGER.info(
        "collection certificate fingerprint: %s", collection.fingerprint
    )
    try:
        secret = collection.secret(private_key)
    except ValueError:
        _LOGGER.error("private key does not match collection archive")
        return
    print(dumps({'filepath': str(filepath), 'secret': secret}))


def _get_secret_cmd(args):
    try:
        private_key = load_private_key(args.private_key)
    except ValueError:
        _LOGGER.error("invalid private key and/or passphrase")
        return
    if not private_key:
        return
    for filepath in args.collections:
        if filepath.is_file():
            _print_collection_secret(private_key, filepath)
            continue
        if filepath.is_dir():
            for item in filepath.glob('Collection_*.zip'):
                _print_collection_secret(private_key, item)
            continue
        _LOGGER.warning("skipped %s", filepath)


def setup_cmd(cmd):
    """Setup get-secret command"""
    get_secret = cmd.add_parser(
        'get-secret', help="get the collection archive secret"
    )
    get_secret.add_argument(
        'private_key',
        type=Path,
        help="private key, given collections must share the same certificate fingerprint",
    )
    get_secret.add_argument(
        'collections',
        metavar='collection',
        nargs='+',
        type=Path,
        help="collection archives",
    )
    get_secret.set_defaults(func=_get_secret_cmd)
