"""Generaptor Profile"""

from dataclasses import dataclass
from json import loads
from pathlib import Path


@dataclass(frozen=True)
class Profile:
    """Profile file"""

    targets: list[str]

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build instance from filepath"""
        data = filepath.read_text(encoding='utf-8')
        dct = loads(data)
        return cls(targets=dct.get('targets', []))


ProfileMapping = dict[str, Profile]
