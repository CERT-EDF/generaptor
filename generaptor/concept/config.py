"""Generaptor Config"""

from dataclasses import dataclass
from gettext import ngettext
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from ..helper.logging import get_logger
from .distribution import OperatingSystem
from .profile import Profile, ProfileMapping
from .ruleset import RuleSet
from .targetset import TargetSet

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
        filepath = self.directory / opsystem.value / 'rules.csv'
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
        filepath = self.directory / opsystem.value / 'targets.csv'
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

    def load_profile_mapping(
        self, opsystem: OperatingSystem
    ) -> ProfileMapping:
        """Load profiles from operating system directory"""
        directory = self.directory / opsystem.value / 'profiles'
        if not directory.is_dir():
            return {}
        mapping = {}
        for filepath in directory.glob('*.json'):
            profile = Profile.from_filepath(filepath)
            if not profile:
                _LOGGER.warning("skipped invalid profile from %s", filepath)
                continue
            mapping[filepath.stem] = profile
        return mapping

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
