"""CustomProfile API
"""
import typing as t
from json import loads
from pathlib import Path
from dataclasses import dataclass


@dataclass
class CustomProfile:
    """Custom profile file"""

    targets: t.List[str]

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build instance from filepath"""
        dct = loads(filepath.read_text())
        return cls(targets=dct.get('targets', []))
