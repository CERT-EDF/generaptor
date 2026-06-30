"""HTTP helpers module.

This module provides HTTP utility functions for downloading and fetching resources.
"""

from json import JSONDecodeError, load
from pathlib import Path
from shutil import copyfileobj
from urllib.request import ProxyHandler, build_opener, install_opener, urlopen

from rich.progress import wrap_file

from .logging import get_logger

_LOGGER = get_logger('helper.http')


def http_set_proxies(proxies):
    """Configure proxies.

    Args:
        proxies (dict): Dictionary of proxy URL mappings.
    """
    _LOGGER.info("using proxies %s", proxies)
    install_opener(build_opener(ProxyHandler(proxies)))


def http_download(url: str, filepath: Path):
    """Download a resource and store it inside a file.

    Args:
        url (str): URL to download from.
        filepath (Path): Local path to save the downloaded content.
    """
    _LOGGER.info("downloading from %s", url)
    with urlopen(url) as response:
        size = int(response.headers['Content-Length'])
        with wrap_file(
            response, total=size, description="Downloading"
        ) as wrapped:
            with filepath.open('wb') as file:
                copyfileobj(wrapped, file)


def http_get_json(url: str):
    """GET a JSON resource.

    Args:
        url (str): URL to fetch JSON from.

    Returns:
        dict | None: Parsed JSON data, or None if request failed or invalid JSON.
    """
    _LOGGER.info("requesting %s", url)
    with urlopen(url) as response:
        if response.status != 200:
            _LOGGER.error("response status %d", response.status)
            return None
        try:
            return load(response)
        except JSONDecodeError:
            _LOGGER.error("failed to decode json data!")
    return None
