"""Generaptor Profile"""

from dataclasses import dataclass
from json import JSONDecodeError, loads
from pathlib import Path

from ..helper.logging import get_logger

_LOGGER = get_logger('concept.profile')


@dataclass(frozen=True)
class Profile:
    """Profile file"""

    targets: list[str]

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build instance from filepath"""
        try:
            dct = loads(filepath.read_text(encoding='utf-8'))
        except (JSONDecodeError, FileNotFoundError, UnicodeDecodeError):
            _LOGGER.exception("cannot load profile from %s", filepath)
            return None
        return cls(targets=dct.get('targets', []))


ProfileMapping = dict[str, Profile]
