"""Github helpers"""

from dataclasses import dataclass
from operator import attrgetter

from .http import http_get_json


@dataclass
class GithubAsset:
    """Github asset data"""

    name: str
    size: int
    url: str
    created_at: str


@dataclass
class GithubRelease:
    """Github release data"""

    name: str
    tag: str
    assets: list[GithubAsset]

    @classmethod
    def from_dict(cls, dct):
        """Contruct instance from dict"""
        return cls(
            name=dct['name'],
            tag=dct['tag_name'],
            assets=sorted(
                [
                    GithubAsset(
                        name=asset['name'],
                        size=asset['size'],
                        url=asset['browser_download_url'],
                        created_at=asset['created_at'],
                    )
                    for asset in dct['assets']
                ],
                key=attrgetter('created_at'),
                reverse=True,
            ),
        )


def github_release(
    owner: str, repository: str, tag: str = 'latest'
) -> GithubRelease | None:
    """Get a summary of the latest release published in a Github repository"""
    page = 1
    while page:
        url = f'https://api.github.com/repos/{owner}/{repository}/releases?per_page=10&page={page}'
        releases = http_get_json(url)
        if not releases:
            return None
        for release in releases:
            if release['draft'] or release['prerelease']:
                continue
            if tag == 'latest':
                return GithubRelease.from_dict(release)
            if tag == release['tag_name']:
                return GithubRelease.from_dict(release)
        page += 1
    return None
