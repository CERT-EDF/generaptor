"""Distribution
"""
from enum import Enum
from dataclasses import dataclass


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


@dataclass
class Distribution:
    """Combination of operating system and architecture"""

    os: OperatingSystem
    arch: Architecture

    def __hash__(self):
        return hash((self.os, self.arch))

    @property
    def suffix(self):
        """Filename suffix"""
        suffix = '-'.join([self.os.value, self.arch.value])
        suffix += '.exe' if self.os == OperatingSystem.WINDOWS else ''
        return suffix

    def match_asset_name(self, name: str):
        """Determine if asset name matches this distribution"""
        return name.endswith(self.suffix)


SUPPORTED_DISTRIBUTIONS = [
    Distribution(OperatingSystem.LINUX, Architecture.AMD64),
    Distribution(OperatingSystem.LINUX, Architecture.AMD64_MUSL),
    Distribution(OperatingSystem.WINDOWS, Architecture.X86),
    Distribution(OperatingSystem.WINDOWS, Architecture.AMD64),
]
