"""Cache APIs
"""

from typing import Optional
from pathlib import Path
from gettext import ngettext
from dataclasses import dataclass
from jinja2 import FileSystemLoader, Environment, Template
from .ruleset import RuleSet
from .targetset import TargetSet
from .distribution import OperatingSystem
from ..helper.logging import LOGGER


@dataclass
class Config:
    """Config directory"""

    directory: Path = Path.home() / '.config' / 'generaptor'

    def load_rule_set(
        self, operating_system: OperatingSystem
    ) -> Optional[RuleSet]:
        """Load rules from cache matching given distribution"""
        filepath = self.directory / f'{operating_system.value}.rules.csv'
        if not filepath.is_file():
            return None
        rule_set = RuleSet.from_filepath(filepath)
        LOGGER.info(
            "loaded %d %s from %s",
            rule_set.count,
            ngettext('rule', 'rules', rule_set.count),
            filepath,
        )
        return rule_set

    def load_target_set(
        self, operating_system: OperatingSystem
    ) -> Optional[TargetSet]:
        """Load targets from cache matching given distribution"""
        filepath = self.directory / f'{operating_system.value}.targets.csv'
        if not filepath.is_file():
            return None
        target_set = TargetSet.from_filepath(filepath)
        LOGGER.info(
            "loaded %d %s from %s",
            target_set.count,
            ngettext('target', 'targets', target_set.count),
            filepath,
        )
        return target_set

    def vql_template(
        self, operating_system: OperatingSystem
    ) -> Optional[Template]:
        """Load jinja template matching given distribution"""
        filename = f'{operating_system.value}.collector.yml.jinja'
        template = self.directory / filename
        if not template.is_file():
            return None
        loader = FileSystemLoader(self.directory)
        environment = Environment(
            loader=loader,
            autoescape=False,  # worst case scenario: we generate invalid YAML
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
        )
        return environment.get_template(filename)
