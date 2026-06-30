"""Generaptor Distribution module.

This module provides enumeration types for architectures and operating systems,
as well as the Distribution class that combines them.
"""

from dataclasses import dataclass
from enum import Enum
from functools import cached_property


class Architecture(Enum):
    """Software architecture.

    Enumeration of supported CPU architectures for Velociraptor distributions.

    Attributes:
        X86: 32-bit x86 architecture.
        AMD64: 64-bit AMD/Intel architecture.
        AMD64_MUSL: 64-bit AMD/Intel architecture with musl libc.
        ARM64: 64-bit ARM architecture.
        X86_LEGACY: Legacy 32-bit x86 architecture.
        AMD64_LEGACY: Legacy 64-bit AMD/Intel architecture.
    """

    X86 = '386'
    AMD64 = 'amd64'
    AMD64_MUSL = 'amd64-musl'
    ARM64 = 'arm64'
    X86_LEGACY = '386-legacy'
    AMD64_LEGACY = 'amd64-legacy'


class OperatingSystem(Enum):
    """Operating system.

    Enumeration of supported operating systems for Velociraptor distributions.

    Attributes:
        WINDOWS: Microsoft Windows operating system.
        DARWIN: Apple macOS/Darwin operating system.
        LINUX: Linux operating system.
        ANDROID: Android mobile operating system.
        IOS: Apple iOS mobile operating system.
    """

    WINDOWS = 'windows'
    DARWIN = 'darwin'
    LINUX = 'linux'
    ANDROID = 'android'
    IOS = 'ios'


@dataclass(kw_only=True, frozen=True)
class Distribution:
    """Combination of operating system and architecture.

    Represents a specific Velociraptor distribution targeting a particular
    operating system and CPU architecture combination.

    Attributes:
        arch (Architecture): The CPU architecture of the distribution.
        opsystem (OperatingSystem): The operating system of the distribution.
    """

    arch: Architecture
    opsystem: OperatingSystem

    @cached_property
    def suffix(self):
        """Filename suffix.

        Returns:
            str: The filename suffix for this distribution, including
                 the appropriate extension (e.g., '.exe' for Windows).
        """
        suffix = '-'.join([self.opsystem.value, self.arch.value])
        if self.opsystem == OperatingSystem.WINDOWS:
            suffix += '.exe'
        return suffix

    def match_asset_name(self, name: str):
        """Determine if asset name matches this distribution.

        Args:
            name (str): The asset filename to check.

        Returns:
            bool: True if the asset name ends with this distribution's suffix.
        """
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
    Distribution(
        arch=Architecture.X86_LEGACY,
        opsystem=OperatingSystem.WINDOWS,
    ),
    Distribution(
        arch=Architecture.AMD64_LEGACY,
        opsystem=OperatingSystem.WINDOWS,
    ),
    Distribution(
        arch=Architecture.AMD64,
        opsystem=OperatingSystem.DARWIN,
    ),
    Distribution(
        arch=Architecture.ARM64,
        opsystem=OperatingSystem.DARWIN,
    ),
]
