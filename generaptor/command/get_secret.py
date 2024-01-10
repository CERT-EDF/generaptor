"""get-secret command
"""
from pathlib import Path
from ..api import Collection
from ..helper.crypto import RSAPrivateKey, load_private_key
from ..helper.logging import LOGGER


def _print_collection_secret(private_key: RSAPrivateKey, filepath: Path):
    collection = Collection(filepath=filepath)
    LOGGER.info(
        "collection certificate fingerprint: %s", collection.fingerprint
    )
    try:
        secret = collection.secret(private_key)
    except ValueError:
        LOGGER.error("Private key does not match collection archive")
        return
    print(f"{secret}:{filepath}")


def _get_secret_cmd(args):
    try:
        private_key = load_private_key(args.private_key)
    except ValueError:
        LOGGER.error("Invalid private key and/or passphrase")
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
        LOGGER.warning("skipped %s", filepath)


def setup_get_secret(cmd):
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
