"""Github helpers
"""
import typing as t
from dataclasses import dataclass
from .http import http_get_json


@dataclass
class GithubAsset:
    """Github asset data"""
    name: str
    size: int
    url: str


@dataclass
class GithubRelease:
    """Github release data"""
    name: str
    tag: str
    assets: t.List[GithubAsset]

    @classmethod
    def from_dict(cls, dct):
        return cls(
            name=dct['name'],
            tag=dct['tag_name'],
            assets=[
                GithubAsset(
                    name=asset['name'],
                    size=asset['size'],
                    url=asset['browser_download_url']
                )
                for asset in dct['assets']
            ],
        )


def github_release(
    owner: str, repository: str, tag: str = 'latest'
) -> GithubRelease:
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
