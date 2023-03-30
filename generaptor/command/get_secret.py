"""get-secret command
"""
from pathlib import Path
from ..helper.crypto import RSAPrivateKey, decrypt_secret, load_private_key
from ..helper.logging import LOGGER
from ..helper.collection import collection_metadata


def _print_collection_secret(private_key: RSAPrivateKey, collection: Path):
    metadata = collection_metadata(collection)
    if not metadata:
        LOGGER.error("failed to retrieve metadata from collection.")
        return
    for field in ('b64_enc_secret', 'fingerprint_hex'):
        if field not in metadata:
            LOGGER.error("metadata field not found: %s", field)
            return
    LOGGER.info(
        "collection certificate fingerprint: %s", metadata['fingerprint_hex']
    )
    b64_enc_secret = metadata['b64_enc_secret']
    secret = decrypt_secret(private_key, b64_enc_secret)
    print(f"{secret.decode()}:{collection}")


def _get_secret_cmd(args):
    private_key = load_private_key(args.private_key)
    if not private_key:
        return
    for collection in args.collections:
        if collection.is_file():
            _print_collection_secret(private_key, collection)
            continue
        if collection.is_dir():
            for item in collection.glob('Collection_*.zip'):
                _print_collection_secret(private_key, item)
            continue
        LOGGER.warning("skipped %s", collection)


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
