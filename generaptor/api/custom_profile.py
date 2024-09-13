"""CustomProfile API
"""

from json import loads
from pathlib import Path
from dataclasses import dataclass


@dataclass
class CustomProfile:
    """Custom profile file"""

    targets: list[str]

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build instance from filepath"""
        dct = loads(filepath.read_text())
        return cls(targets=dct.get('targets', []))
