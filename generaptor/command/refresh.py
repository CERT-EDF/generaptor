"""refresh command
"""
from ..api import SUPPORTED_DISTRIBUTIONS
from ..helper.http import http_set_proxies, http_download
from ..helper.prompt import confirm
from ..helper.github import github_release
from ..helper.logging import LOGGER


def _refresh_cmd(args):
    if not (args.yes or confirm("Refreshing cache will flush current cache.")):
        return
    LOGGER.info("refreshing cache...")
    args.cache.flush(args.refresh_config, args.do_not_fetch)
    args.cache.ensure()
    if args.do_not_fetch:
        return
    LOGGER.info("downloading %s release...", args.fetch_tag)
    if args.proxy_url:
        http_set_proxies({'https': args.proxy_url})
    gh_release = github_release('velocidex', 'velociraptor', args.fetch_tag)
    if not gh_release:
        LOGGER.error("failed to find a valid realease for tag: %s", args.fetch_tag)
        return
    LOGGER.info("velociraptor release matched: %s", gh_release.tag)
    downloaded = set()
    for asset in gh_release.assets:
        for distrib in SUPPORTED_DISTRIBUTIONS:
            if distrib in downloaded:
                continue
            if not distrib.match_asset_name(asset.name):
                continue
            downloaded.add(distrib)
            LOGGER.info(
                "%s matched asset '%s' (size=%d)",
                distrib,
                asset.name,
                asset.size,
            )
            http_download(asset.url, args.cache.path(asset.url.split('/')[-1]))


def setup_refresh(cmd):
    """Setup refresh command"""
    refresh = cmd.add_parser('refresh', help="refresh environment cache")
    refresh.add_argument(
        '--yes', '-y', action='store_true', help="non-interactive confirmation"
    )
    refresh.add_argument(
        '--refresh-config',
        action='store_true',
        help="refresh configuration files as well",
    )
    refresh.add_argument(
        '--do-not-fetch',
        action='store_true',
        help="do not fetch latest velociraptor release",
    )
    refresh.add_argument(
        '--fetch-tag',
        default='v0.7.0',
        help=(
            "fetch this tag, use 'latest' to fetch the latest version, warning:"
            " fecthing another version than the default might break the collector"
        ),
    )
    refresh.add_argument('--proxy-url', help="set proxy url")
    refresh.set_defaults(func=_refresh_cmd)
