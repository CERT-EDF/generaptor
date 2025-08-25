"""Generaptor Distribution"""

from dataclasses import dataclass
from enum import Enum
from functools import cached_property


class Architecture(Enum):
    """Software architecture"""

    X86 = '386'
    AMD64 = 'amd64'
    AMD64_MUSL = 'amd64-musl'
    ARM64 = 'arm64'


class OperatingSystem(Enum):
    """Operating system"""

    WINDOWS = 'windows'
    DARWIN = 'darwin'
    LINUX = 'linux'
    ANDROID = 'android'
    IOS = 'ios'


@dataclass(kw_only=True, frozen=True)
class Distribution:
    """Combination of operating system and architecture"""

    arch: Architecture
    opsystem: OperatingSystem

    @cached_property
    def suffix(self):
        """Filename suffix"""
        suffix = '-'.join([self.opsystem.value, self.arch.value])
        if self.opsystem == OperatingSystem.WINDOWS:
            suffix += '.exe'
        return suffix

    def match_asset_name(self, name: str):
        """Determine if asset name matches this distribution"""
        return name.endswith(self.suffix)


SUPPORTED_DISTRIBUTIONS = [
    Distribution(
        arch=Architecture.AMD64,
        opsystem=OperatingSystem.LINUX,
    ),
    Distribution(
        arch=Architecture.AMD64_MUSL,
        opsystem=OperatingSystem.LINUX,
    ),
    Distribution(
        arch=Architecture.X86,
        opsystem=OperatingSystem.WINDOWS,
    ),
    Distribution(
        arch=Architecture.AMD64,
        opsystem=OperatingSystem.WINDOWS,
    ),
]
