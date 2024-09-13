"""Distribution API
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


DEFAULT_OS_TARGETS_MAPPING = {
    OperatingSystem.WINDOWS: ['Triage/Kape'],
    OperatingSystem.LINUX: ['Triage/Full'],
}


@dataclass
class Distribution:
    """Combination of operating system and architecture"""

    architecture: Architecture
    operating_system: OperatingSystem

    def __hash__(self):
        return hash((self.architecture, self.operating_system))

    @property
    def suffix(self):
        """Filename suffix"""
        suffix = '-'.join(
            [self.operating_system.value, self.architecture.value]
        )
        if self.operating_system == OperatingSystem.WINDOWS:
            suffix += '.exe'
        return suffix

    def match_asset_name(self, name: str):
        """Determine if asset name matches this distribution"""
        return name.endswith(self.suffix)


SUPPORTED_DISTRIBUTIONS = [
    Distribution(
        operating_system=OperatingSystem.LINUX,
        architecture=Architecture.AMD64,
    ),
    Distribution(
        operating_system=OperatingSystem.LINUX,
        architecture=Architecture.AMD64_MUSL,
    ),
    Distribution(
        operating_system=OperatingSystem.WINDOWS,
        architecture=Architecture.X86,
    ),
    Distribution(
        operating_system=OperatingSystem.WINDOWS,
        architecture=Architecture.AMD64,
    ),
]
