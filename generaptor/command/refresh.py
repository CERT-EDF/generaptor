"""refresh command
"""
from ..helper.http import http_set_proxies, http_download
from ..helper.prompt import confirm
from ..helper.github import github_latest_release
from ..helper.logging import LOGGER
from ..helper.distrib import SUPPORTED_DISTRIBUTIONS


def _refresh_cmd(args):
    if not confirm("Refreshing cache will flush current cache."):
        return
    LOGGER.info("refreshing cache...")
    args.cache.flush(args.refresh_config, args.do_not_fetch)
    args.cache.ensure()
    if args.do_not_fetch:
        return
    LOGGER.info("downloading latest stable release...")
    if args.proxy_url:
        http_set_proxies({'https': args.proxy_url})
    release = github_latest_release('velocidex', 'velociraptor')
    downloaded = set()
    for asset in release['assets']:
        for distrib in SUPPORTED_DISTRIBUTIONS:
            if distrib in downloaded:
                continue
            if not distrib.match_asset_name(asset['name']):
                continue
            downloaded.add(distrib)
            LOGGER.info(
                "%s matched asset '%s' (size=%d)",
                distrib,
                asset['name'],
                asset['size'],
            )
            url = asset['browser_download_url']
            http_download(url, args.cache.path(url.split('/')[-1]))


def setup_refresh(cmd):
    """Setup refresh command"""
    refresh = cmd.add_parser('refresh', help="refresh environment cache")
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
    refresh.add_argument('--proxy-url', help="set proxy url")
    refresh.set_defaults(func=_refresh_cmd)
