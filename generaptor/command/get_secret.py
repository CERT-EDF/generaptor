"""get-secret command module.

This module provides the CLI command for retrieving decrypted secrets
from collection archives using private keys.
"""

from pathlib import Path

from ..concept import Collection
from ..helper.crypto import RSAPrivateKey, load_private_key
from ..helper.json import dump_json
from ..helper.logging import get_logger

_LOGGER = get_logger('command.get_secret')


def _print_collection_secret(private_key: RSAPrivateKey, filepath: Path):
    """Print collection secret as JSON.

    Args:
        private_key (RSAPrivateKey): Private key for decrypting the secret.
        filepath (Path): Path to the collection archive file.
    """
    collection = Collection(filepath=filepath)
    _LOGGER.info(
        "collection certificate fingerprint: %s", collection.fingerprint
    )
    try:
        secret = collection.secret(private_key)
    except ValueError:
        _LOGGER.error("private key does not match collection archive")
        return
    print(dump_json({'filepath': str(filepath), 'secret': secret}))


def _get_secret_cmd(args):
    """Handle get-secret command execution.

    Args:
        args: Parsed command line arguments with private_key and collections paths.
    """
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
    """Setup get-secret command.

    Args:
        cmd: argparse subparsers object to add the command to.
    """
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
