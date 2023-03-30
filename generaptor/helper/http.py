"""HTTP helpers
"""
from json import load, JSONDecodeError
from shutil import copyfileobj
from pathlib import Path
from urllib.request import (
    install_opener,
    build_opener,
    urlopen,
    ProxyHandler,
)
from rich.progress import wrap_file
from .logging import LOGGER


def http_set_proxies(proxies):
    """Configure proxies"""
    LOGGER.info("using proxies %s", proxies)
    install_opener(build_opener(ProxyHandler(proxies)))


def http_download(url: str, filepath: Path):
    """Download a resource and store it inside a file"""
    LOGGER.info("downloading from %s", url)
    with urlopen(url) as response:
        size = int(response.headers['Content-Length'])
        with wrap_file(
            response, total=size, description="Downloading"
        ) as wrapped:
            with filepath.open('wb') as file:
                copyfileobj(wrapped, file)


def http_get_json(url: str):
    """GET a JSON resource"""
    LOGGER.info("requesting %s", url)
    with urlopen(url) as response:
        if response.status != 200:
            LOGGER.error("response status %d", response.status)
            return None
        try:
            return load(response)
        except JSONDecodeError:
            LOGGER.error("failed to decode json data!")
    return None
