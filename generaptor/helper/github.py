"""Github helpers
"""
from .http import http_get_json


def github_latest_release(owner: str, repository: str):
    """Get a summary of the latest release published in a Github repository"""
    page = 1
    while page:
        url = f'https://api.github.com/repos/{owner}/{repository}/releases?per_page=10&page={page}'
        releases = http_get_json(url)
        if not releases:
            return None
        for release in releases:
            if release['draft'] or release['prerelease']:
                page += 1
                continue
            return {
                'name': release['name'],
                'assets': [
                    {
                        'name': asset['name'],
                        'size': asset['size'],
                        'browser_download_url': asset['browser_download_url'],
                    }
                    for asset in release['assets']
                ],
            }
