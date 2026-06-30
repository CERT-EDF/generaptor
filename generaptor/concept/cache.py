"""Generaptor Cache module.

This module provides cache management functionality for generaptor,
including cache directory handling and binary distribution management.
"""

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from platform import architecture, libc_ver, machine, system
from shutil import copytree

from ..helper.logging import get_logger
from .config import Config
from .distribution import Architecture, Distribution, OperatingSystem

_LOGGER = get_logger('concept.cache')
_HERE = Path(__file__).resolve()
_PKG_DATA_DIR = _HERE.parent.parent / 'data'


def _darwin_identify_dist() -> Distribution:
    """Identify macOS/Darwin distribution.

    Returns:
        Distribution: Distribution object for the current macOS system.
    """
    arch = machine().lower()
    if 'arm' in arch:
        return Distribution(
            arch=Architecture.ARM64, opsystem=OperatingSystem.DARWIN
        )
    return Distribution(
        arch=Architecture.AMD64, opsystem=OperatingSystem.DARWIN
    )


def _linux_identify_dist() -> Distribution:
    """Identify Linux distribution.

    Returns:
        Distribution: Distribution object for the current Linux system.
    """
    lib, _ = libc_ver()
    if lib == 'glibc':
        return Distribution(
            arch=Architecture.AMD64, opsystem=OperatingSystem.LINUX
        )
    return Distribution(
        arch=Architecture.AMD64_MUSL, opsystem=OperatingSystem.LINUX
    )


def _windows_identify_dist() -> Distribution:
    """Identify Windows distribution.

    Returns:
        Distribution: Distribution object for Windows (always AMD64).
    """
    return Distribution(
        arch=Architecture.AMD64, opsystem=OperatingSystem.WINDOWS
    )


_SYSTEM_IDENTIFY_DIST_MAP = {
    'Darwin': _darwin_identify_dist,
    'Linux': _linux_identify_dist,
    'Windows': _windows_identify_dist,
}


@dataclass(frozen=True)
class Cache:
    """Cache directory.

    Manages the cache directory for generaptor, including program binaries
    and configuration files.

    Attributes:
        directory (Path): Path to the cache directory.
    """

    directory: Path = Path.home() / '.cache' / 'generaptor'

    @classmethod
    def from_string(cls, directory: str):
        """Create instance from string.

        Args:
            directory (str): String path to the cache directory.

        Returns:
            Cache: Cache instance with resolved directory path.
        """
        return cls(Path(directory).resolve())

    @cached_property
    def config(self) -> Config:
        """Cache config.

        Returns:
            Config: Configuration loaded from the cache directory.
        """
        return Config(self.directory / 'config')

    @cached_property
    def program(self):
        """Cache program directory.

        Returns:
            Path: Path to the program subdirectory within the cache.
        """
        return self.directory / 'program'

    def path(self, filename: str) -> Path | None:
        """Generate program path for filename.

        Args:
            filename (str): The filename to create a path for.

        Returns:
            Path | None: Resolved path within program directory, or None if path traversal detected.
        """
        filepath = (self.program / filename).resolve()
        if not filepath.is_relative_to(self.program):
            _LOGGER.warning("path traversal attempt!")
            return None
        return filepath

    def update(self, do_not_fetch: bool = False) -> bool:
        """Ensure that the cache directory is valid and mandatory files are present.

        Args:
            do_not_fetch (bool): If True, skip fetching new files even if cache is empty.

        Returns:
            bool: True if cache was successfully updated.
        """
        if self.program.is_dir() and not do_not_fetch:
            for filepath in self.program.iterdir():
                filepath.unlink()
        self.program.mkdir(parents=True, exist_ok=True)
        copytree(_PKG_DATA_DIR, self.directory, dirs_exist_ok=True)
        return True

    def template_binary(self, dist: Distribution) -> Path | None:
        """Return template binary for distrib.

        Args:
            dist (Distribution): The distribution to find the binary for.

        Returns:
            Path | None: Path to the binary matching the distribution suffix, or None if not found.
        """
        try:
            return next(self.program.glob(f'*{dist.suffix}'))
        except StopIteration:
            _LOGGER.critical(
                "distribution file not found in cache! Please update the cache"
            )
            return None

    def platform_binary(self) -> Path | None:
        """Platform binary to be used to produce collectors.

        Automatically identifies the current platform's architecture and OS
        to return the appropriate binary.

        Returns:
            Path | None: Path to the platform-specific binary, or None if not supported.
        """
        bits, _ = architecture()
        if bits != '64bit':
            _LOGGER.critical("current machine architecture is not supported!")
            return None
        identify_dist = _SYSTEM_IDENTIFY_DIST_MAP.get(system())
        if not identify_dist:
            _LOGGER.critical("current machine distribution is not supported!")
            return None
        distribution = identify_dist()
        if not distribution:
            _LOGGER.critical("current machine distribution is not supported!")
            return None
        return self.template_binary(distribution)
