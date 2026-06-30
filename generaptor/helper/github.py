"""Github helpers module.

This module provides GitHub API integration for fetching release information
and asset details from GitHub repositories.
"""

from dataclasses import dataclass
from operator import attrgetter

from .http import http_get_json


@dataclass
class GithubAsset:
    """Github asset data.

    Represents a GitHub release asset with metadata.

    Attributes:
        name (str): Name of the asset.
        size (int): Size of the asset in bytes.
        url (str): Download URL for the asset.
        created_at (str): Creation timestamp of the asset.
    """

    name: str
    size: int
    url: str
    created_at: str


@dataclass
class GithubRelease:
    """Github release data.

    Represents a GitHub repository release with its assets.

    Attributes:
        name (str): Name of the release.
        tag (str): Tag name of the release.
        assets (list[GithubAsset]): List of assets in this release, sorted by creation date.
    """

    name: str
    tag: str
    assets: list[GithubAsset]

    @classmethod
    def from_dict(cls, dct):
        """Contruct instance from dict.

        Args:
            dct (dict): Dictionary containing release data from GitHub API.

        Returns:
            GithubRelease: GithubRelease instance with parsed and sorted assets.
        """
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
    """Get a summary of the latest release published in a Github repository.

    Args:
        owner (str): Repository owner/organization name.
        repository (str): Repository name.
        tag (str): Release tag to fetch. Defaults to 'latest' for most recent non-draft release.

    Returns:
        GithubRelease | None: GitHub release information, or None if not found.
    """
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
