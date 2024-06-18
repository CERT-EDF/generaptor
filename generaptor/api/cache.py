"""Cache APIs
"""
import typing as t
from shutil import copy
from pathlib import Path
from gettext import ngettext
from platform import system, architecture
from dataclasses import dataclass
from jinja2 import FileSystemLoader, Environment, Template
from .ruleset import RuleSet
from .targetset import TargetSet
from .distribution import Distribution, OperatingSystem, Architecture
from ..helper.logging import LOGGER


_HERE = Path(__file__).resolve()
_PKG_DATA_DIR = _HERE.parent.parent / 'data'
_PLATFORM_DISTRIBUTION_MAP = {
    'Linux': Distribution(
        operating_system=OperatingSystem.LINUX, architecture=Architecture.AMD64
    ),
    'Windows': Distribution(
        operating_system=OperatingSystem.WINDOWS,
        architecture=Architecture.AMD64,
    ),
}


def _copy_pkg_data_to_cache(pattern, cache_dir):
    for src_path in _PKG_DATA_DIR.glob(pattern):
        copy(src_path, cache_dir / src_path.name)


@dataclass
class Cache:
    """Cache directory"""

    directory: Path = Path.home() / '.cache' / 'generaptor'

    @property
    def program(self):
        """Cache program directory"""
        return self.directory / 'program'

    def path(self, filename: str) -> Path:
        """Generate program path for filename"""
        filepath = (self.program / filename).resolve()
        if not filepath.is_relative_to(self.program):
            LOGGER.warning("path traversal attempt!")
            return None
        return filepath

    def update(self, do_not_fetch: bool = False) -> bool:
        """Ensure that the cache directory is valid and mandatory files are present"""
        if self.program.is_dir() and not do_not_fetch:
            for filepath in self.program.iterdir():
                filepath.unlink()
        self.program.mkdir(parents=True, exist_ok=True)
        _copy_pkg_data_to_cache('*.collector.yml', self.directory)
        _copy_pkg_data_to_cache('*.targets.csv', self.directory)
        _copy_pkg_data_to_cache('*.rules.csv', self.directory)
        return True

    def load_rule_set(
        self, operating_system: OperatingSystem
    ) -> t.Optional[RuleSet]:
        """Load rules from cache matching given distribution"""
        filepath = self.directory / f'{operating_system.value}.rules.csv'
        if not filepath.is_file():
            LOGGER.warning("file not found: %s", filepath)
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
    ) -> t.Optional[TargetSet]:
        """Load targets from cache matching given distribution"""
        filepath = self.directory / f'{operating_system.value}.targets.csv'
        if not filepath.is_file():
            LOGGER.warning("file not found: %s", filepath)
            return None
        target_set = TargetSet.from_filepath(filepath)
        LOGGER.info(
            "loaded %d %s from %s",
            target_set.count,
            ngettext('target', 'targets', target_set.count),
            filepath,
        )
        return target_set

    def vql_template(self, operating_system: OperatingSystem) -> Template:
        """Load jinja template matching given distribution"""
        loader = FileSystemLoader(self.directory)
        environment = Environment(
            loader=loader,
            autoescape=False,  # worst case scenario: we generate invalid YAML
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
        )
        return environment.get_template(
            f'{operating_system.value}.collector.yml'
        )

    def template_binary(self, dist: Distribution) -> t.Optional[Path]:
        """Return template binary for distrib"""
        try:
            return next(self.program.glob(f'*{dist.suffix}'))
        except StopIteration:
            LOGGER.critical(
                "distribution file not found in cache! Please update the cache"
            )
            return None

    def platform_binary(self) -> t.Optional[Path]:
        """Platform binary to be used to produce collectors"""
        if architecture()[0] != '64bit':
            LOGGER.critical("current machine architecture is not supported!")
            return None
        dist = _PLATFORM_DISTRIBUTION_MAP.get(system())
        if not dist:
            LOGGER.critical("current machine distribution is not supported!")
            return None
        return self.template_binary(dist)
