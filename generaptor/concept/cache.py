"""Generaptor Cache"""

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from platform import architecture, libc_ver, system
from shutil import copytree

from ..helper.logging import get_logger
from .config import Config
from .distribution import Architecture, Distribution, OperatingSystem

_LOGGER = get_logger('concept.cache')
_HERE = Path(__file__).resolve()
_PKG_DATA_DIR = _HERE.parent.parent / 'data'
_PLATFORM_DISTRIBUTION_MAP = {
    ('Linux', 'glibc'): Distribution(
        arch=Architecture.AMD64, opsystem=OperatingSystem.LINUX
    ),
    ('Linux', ''): Distribution(
        arch=Architecture.AMD64_MUSL, opsystem=OperatingSystem.LINUX
    ),
    ('Windows', ''): Distribution(
        arch=Architecture.AMD64, opsystem=OperatingSystem.WINDOWS
    ),
}


@dataclass(frozen=True)
class Cache:
    """Cache directory"""

    directory: Path = Path.home() / '.cache' / 'generaptor'

    @classmethod
    def from_string(cls, directory: str):
        """Create instance from string"""
        return cls(Path(directory).resolve())

    @cached_property
    def config(self) -> Config:
        """Cache config"""
        return Config(self.directory / 'config')

    @cached_property
    def program(self):
        """Cache program directory"""
        return self.directory / 'program'

    def path(self, filename: str) -> Path | None:
        """Generate program path for filename"""
        filepath = (self.program / filename).resolve()
        if not filepath.is_relative_to(self.program):
            _LOGGER.warning("path traversal attempt!")
            return None
        return filepath

    def update(self, do_not_fetch: bool = False) -> bool:
        """Ensure that the cache directory is valid and mandatory files are present"""
        if self.program.is_dir() and not do_not_fetch:
            for filepath in self.program.iterdir():
                filepath.unlink()
        self.program.mkdir(parents=True, exist_ok=True)
        copytree(_PKG_DATA_DIR, self.directory, dirs_exist_ok=True)
        return True

    def template_binary(self, dist: Distribution) -> Path | None:
        """Return template binary for distrib"""
        try:
            return next(self.program.glob(f'*{dist.suffix}'))
        except StopIteration:
            _LOGGER.critical(
                "distribution file not found in cache! Please update the cache"
            )
            return None

    def platform_binary(self) -> Path | None:
        """Platform binary to be used to produce collectors"""
        bits, _ = architecture()
        if bits != '64bit':
            _LOGGER.critical("current machine architecture is not supported!")
            return None
        lib, _ = libc_ver()
        platform_distrib_id = (system(), lib)
        dist = _PLATFORM_DISTRIBUTION_MAP.get(platform_distrib_id)
        if not dist:
            _LOGGER.critical("current machine distribution is not supported!")
            return None
        return self.template_binary(dist)
