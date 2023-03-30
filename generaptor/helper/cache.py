"""Cache helpers
"""
import typing as t
from csv import reader
from json import loads
from shutil import copy
from pathlib import Path
from platform import system, architecture
from dataclasses import dataclass
from jinja2 import FileSystemLoader, Environment, Template
from .logging import LOGGER
from .distrib import Distribution, OperatingSystem, Architecture


HERE = Path(__file__).resolve()
PKG_DATA_DIR = HERE.parent.parent / 'data'
PLATFORM_DISTRIB_MAP = {
    'Linux': Distribution(OperatingSystem.LINUX, Architecture.AMD64),
    'Windows': Distribution(OperatingSystem.WINDOWS, Architecture.AMD64),
}


def _stream_csv(csv_filepath: Path):
    with csv_filepath.open(newline='') as csv_fp:
        csv_reader = reader(csv_fp, delimiter=',', quotechar='"')
        try:
            next(csv_reader)  # skip csv header
        except StopIteration:
            return
        for row in csv_reader:
            yield row


def _copy_pkg_data_to_cache(pattern, cache_dir):
    for src_path in PKG_DATA_DIR.glob(pattern):
        dst_path = cache_dir / src_path.name
        if not dst_path.is_file():
            copy(src_path, dst_path)


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

    def flush(self, update_config=False, do_not_fetch=False):
        """Flush cached config and/or programs"""
        if self.program.is_dir() and not do_not_fetch:
            for filepath in self.program.iterdir():
                filepath.unlink()
        if self.directory.is_dir() and update_config:
            for filepath in self.directory.iterdir():
                if not filepath.is_file():
                    continue
                filepath.unlink()

    def ensure(self) -> bool:
        """Ensure that the cache directory is valid and mandatory files are present"""
        # attempt to create directory anyway
        self.program.mkdir(parents=True, exist_ok=True)
        # copy configuration templates
        _copy_pkg_data_to_cache('*.collector.yml', self.directory)
        # copy targets datasets
        _copy_pkg_data_to_cache('*.targets.csv', self.directory)
        # copy rules datasets
        _copy_pkg_data_to_cache('*.rules.csv', self.directory)
        return True

    def load_rules(self, distrib: Distribution):
        """Load rules from cache matching given distribution"""
        filepath = self.directory / f'{distrib.os.value}.rules.csv'
        rules = {int(row[0]): row[1:] for row in _stream_csv(filepath)}
        LOGGER.info("loaded %d rules.", len(rules))
        return rules

    def load_targets(self, distrib: Distribution):
        """Load targets from cache matching given distribution"""
        filepath = self.directory / f'{distrib.os.value}.targets.csv'
        targets = {}
        for row in _stream_csv(filepath):
            targets[row[0]] = set(loads(row[1]))
        LOGGER.info("loaded %d targets.", len(targets))
        return targets

    def template_config(self, distrib: Distribution) -> Template:
        """Load jinja template matching given distribution"""
        loader = FileSystemLoader(self.directory)
        environment = Environment(
            loader=loader,
            autoescape=False,  # worst case scenario: we generate invalid YAML
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
        )
        return environment.get_template(f'{distrib.os.value}.collector.yml')

    def template_binary(self, distrib: Distribution) -> t.Optional[Path]:
        """Return template binary for distrib"""
        try:
            return next(self.program.glob(f'*{distrib.suffix}'))
        except StopIteration:
            LOGGER.critical(
                "distribution file not found in cache! Please update the cache."
            )
            return None

    def platform_binary(self) -> t.Optional[Path]:
        """Platform binary to be used to produce collectors"""
        if architecture()[0] != '64bit':
            LOGGER.critical("current machine architecture is not supported!")
            return None
        distrib = PLATFORM_DISTRIB_MAP.get(system())
        if not distrib:
            LOGGER.critical("current machine distribution is not supported!")
            return None
        return self.template_binary(distrib)
