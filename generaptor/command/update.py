"""update command module.

This module provides the CLI command for updating the cache and fetching
Velociraptor binaries from GitHub releases.
"""

from semver import Version

from ..concept import SUPPORTED_DISTRIBUTIONS
from ..helper.github import github_releases, version_from_tag
from ..helper.http import http_download, http_set_proxies
from ..helper.logging import get_logger

_LOGGER = get_logger('command.update')
_DEFAULT_VERSION = Version(0, 77, 0)


def _update_cmd(args):
    """Handle update command execution.

    Args:
        args: Parsed command line arguments with cache, download flag, version, and proxy settings.
    """
    _LOGGER.info("updating...")
    args.cache.update(args.no_download)
    _LOGGER.info("cache updated.")
    if args.no_download:
        return
    _LOGGER.info("searching for releases related to %s", args.version)
    if args.proxy_url:
        http_set_proxies({'https': args.proxy_url})
    gh_releases = github_releases('velocidex', 'velociraptor', args.version)
    if not gh_releases:
        _LOGGER.error(
            "failed to find a release matching version %s", args.version
        )
        return
    downloaded = set()
    for gh_release in gh_releases:
        _LOGGER.info(
            "searching for required assets in release %s", gh_release.version
        )
        for asset in gh_release.assets:
            for distrib in SUPPORTED_DISTRIBUTIONS:
                if distrib in downloaded:
                    continue
                if not distrib.match_asset_name(asset.name):
                    continue
                downloaded.add(distrib)
                _LOGGER.info(
                    "%s matched asset '%s' (size=%d)",
                    distrib,
                    asset.name,
                    asset.size,
                )
                http_download(
                    asset.url, args.cache.path(asset.url.split('/')[-1])
                )


def setup_cmd(cmd):
    """Setup update command.

    Args:
        cmd: argparse subparsers object to add the command to.
    """
    update = cmd.add_parser('update', help="update config and fetch binaries")
    update.add_argument(
        '--no-download',
        action='store_true',
        help="do not download velociraptor binaries",
    )
    update.add_argument(
        '--version',
        type=version_from_tag,
        default=_DEFAULT_VERSION,
        help=(
            "Velociraptor version to download. Caution, downloading "
            "another version than the default may break the collector. "
            f"Default version is {_DEFAULT_VERSION}"
        ),
    )
    update.add_argument('--proxy-url', help="set proxy url")
    update.set_defaults(func=_update_cmd)
