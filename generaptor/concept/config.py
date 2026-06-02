"""Generaptor Config"""

from dataclasses import dataclass
from gettext import ngettext
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from ..helper.logging import get_logger
from .distribution import OperatingSystem
from .profile_set import ProfileSet
from .rule_set import RuleSet
from .target_set import TargetSet

_LOGGER = get_logger('concept.config')


@dataclass(frozen=True)
class Config:
    """Config directory"""

    directory: Path = Path.home() / '.config' / 'generaptor'

    @classmethod
    def from_string(cls, directory: str):
        """Create instance from string"""
        return cls(Path(directory).resolve())

    def load_rule_set(self, opsystem: OperatingSystem) -> RuleSet | None:
        """Load rules from operating system directory"""
        filepath = self.directory / opsystem.value / 'rules.jsonl'
        if not filepath.is_file():
            return None
        rule_set = RuleSet.from_filepath(filepath)
        _LOGGER.info(
            "loaded %d %s from %s",
            rule_set.count,
            ngettext('rule', 'rules', rule_set.count),
            filepath,
        )
        return rule_set

    def load_target_set(self, opsystem: OperatingSystem) -> TargetSet | None:
        """Load targets from operating system directory"""
        filepath = self.directory / opsystem.value / 'targets.jsonl'
        if not filepath.is_file():
            return None
        target_set = TargetSet.from_filepath(filepath)
        _LOGGER.info(
            "loaded %d %s from %s",
            target_set.count,
            ngettext('target', 'targets', target_set.count),
            filepath,
        )
        return target_set

    def load_profile_set(self, opsystem: OperatingSystem) -> ProfileSet | None:
        """Load profiles from operating system directory"""
        filepath = self.directory / opsystem.value / 'profiles.jsonl'
        if not filepath.is_file():
            return None
        profile_set = ProfileSet.from_filepath(filepath)
        _LOGGER.info(
            "loaded %d %s from %s",
            profile_set.count,
            ngettext('profile', 'profiles', profile_set.count),
            filepath,
        )
        return profile_set

    def vql_template(self, opsystem: OperatingSystem) -> Template | None:
        """Load jinja template matching given operating system"""
        template = self.directory / opsystem.value / 'collector.yml.jinja'
        if not template.is_file():
            return None
        loader = FileSystemLoader(template.parent)
        environment = Environment(
            loader=loader,
            autoescape=False,  # worst case scenario: we generate invalid YAML
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
        )
        return environment.get_template(template.name)
