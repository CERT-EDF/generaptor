"""refresh command"""

from ..concept import SUPPORTED_DISTRIBUTIONS
from ..helper.github import github_release
from ..helper.http import http_download, http_set_proxies
from ..helper.logging import get_logger

_LOGGER = get_logger('command.update')


def _update_cmd(args):
    _LOGGER.info("updating...")
    args.cache.update(args.do_not_fetch)
    _LOGGER.info("cache updated.")
    if args.do_not_fetch:
        return
    _LOGGER.info("downloading %s release...", args.fetch_tag)
    if args.proxy_url:
        http_set_proxies({'https': args.proxy_url})
    gh_release = github_release('velocidex', 'velociraptor', args.fetch_tag)
    if not gh_release:
        _LOGGER.error(
            "failed to find a valid realease for tag: %s", args.fetch_tag
        )
        return
    _LOGGER.info("velociraptor release matched: %s", gh_release.tag)
    downloaded = set()
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
            http_download(asset.url, args.cache.path(asset.url.split('/')[-1]))


def setup_cmd(cmd):
    """Setup update command"""
    update = cmd.add_parser('update', help="update config and fetch binaries")
    update.add_argument(
        '--do-not-fetch',
        action='store_true',
        help="do not fetch velociraptor binaries",
    )
    update.add_argument(
        '--fetch-tag',
        default='v0.74',
        help=(
            "fetch this tag, use 'latest' to fetch the latest version. "
            "Caution: fecthing another version than the default might "
            "break the collector"
        ),
    )
    update.add_argument('--proxy-url', help="set proxy url")
    update.set_defaults(func=_update_cmd)
