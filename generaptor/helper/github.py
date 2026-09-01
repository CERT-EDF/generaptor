"""Github helpers module.

This module provides GitHub API integration for fetching release information
and asset details from GitHub repositories.
"""

from dataclasses import dataclass
from operator import attrgetter

from semver import Version

from .http import http_get_json


def version_from_tag(tag: str) -> Version:
    """Best effort parsing for non semver tag names.

    Args:
        tag (str): Tag or version to convert to semver Version.

    Returns:
        Version: Version resulting from parsing.
    """
    tag = tag.lstrip('v')
    if tag.count('.') == 1:
        tag += '.0'
    return Version.parse(tag)


def is_compatible(a: Version, b: Version) -> bool:
    """Determine if version a and b are compatible.

    Args:
        a (Version): From version
        b (Version): To version

    Returns:
        True if versions are theorically compatible else False
    """
    if a.major == b.major == 0:
        s_a = Version(a.minor, a.patch, 0)
        s_b = Version(b.minor, b.patch, 0)
        return s_a.is_compatible(s_b)
    return a.is_compatible(b)


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
        version (Version): Version of the release.
        assets (list[GithubAsset]): List of assets in this release, sorted by creation date.
    """

    name: str
    version: Version
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
            version=version_from_tag(dct['tag_name']),
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


def github_releases(
    owner: str, repository: str, version: Version
) -> list[GithubRelease]:
    """Get a list of all compatible releases ordered by version desc.

    Args:
        owner (str): Repository owner/organization name.
        repository (str): Repository name.
        version (Version): Release version to fetch (including latest patches).

    Returns:
        list[GithubRelease]: Matched GitHub releases, empty if no matching release found.
    """
    releases = []
    url = f'https://api.github.com/repos/{owner}/{repository}/releases?per_page=50'
    body = http_get_json(url)
    if not body:
        return []
    for release in body:
        if release['draft'] or release['prerelease']:
            continue
        release = GithubRelease.from_dict(release)
        if not is_compatible(version, release.version):
            continue
        releases.append(release)
    return list(sorted(releases, key=attrgetter('version'), reverse=True))
