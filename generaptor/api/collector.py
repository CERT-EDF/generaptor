"""Collector API
"""
import typing as t
from io import StringIO
from csv import writer, QUOTE_MINIMAL
from pathlib import Path
from platform import system
from datetime import datetime
from subprocess import run
from dataclasses import dataclass
from .cache import Cache
from .config import Config
from .ruleset import RuleSet
from .distribution import Distribution, OperatingSystem
from ..helper.crypto import Certificate, fingerprint, pem_string
from ..helper.logging import LOGGER


def _globs_from_ruleset(rule_set: RuleSet):
    imstr = StringIO()
    csv_writer = writer(
        imstr, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL
    )
    for rule in rule_set.rules.values():
        csv_writer.writerow([rule.glob, rule.accessor])
    file_globs = imstr.getvalue()
    imstr.close()
    return file_globs


@dataclass
class CollectorConfig:
    """Collector configuration"""

    device: str
    rule_set: RuleSet
    certificate: Certificate
    distribution: Distribution
    dont_be_lazy: t.Optional[bool] = None
    vss_analysis_age: t.Optional[int] = None
    use_auto_accessor: t.Optional[bool] = None

    @property
    def context(self):
        """Context for jinja template engine"""
        ctx = {
            'device': self.device,
            'cert_data_pem_str': pem_string(self.certificate),
            'cert_fingerprint_hex': fingerprint(self.certificate),
            'file_globs': _globs_from_ruleset(self.rule_set),
        }
        if self.distribution.operating_system == OperatingSystem.WINDOWS:
            ctx['dont_be_lazy'] = 'Y' if self.dont_be_lazy else 'N'
            ctx['vss_analysis_age'] = self.vss_analysis_age
            ctx['use_auto_accessor'] = 'Y' if self.use_auto_accessor else 'N'
        return ctx

    def generate(self, cache: Cache, config: Config, filepath: Path):
        """Generate configuration file data"""
        vql_template = config.vql_template(
            self.distribution.operating_system
        )
        if vql_template is None:
            vql_template = cache.vql_template(
                self.distribution.operating_system
            )
        else:
            LOGGER.warning("using custom VQL template...")
        with filepath.open('wb') as fstream:
            stream = vql_template.stream(self.context)
            stream.dump(fstream, encoding='utf-8')


@dataclass
class Collector:
    """Collector"""

    config: CollectorConfig

    def generate(
        self, cache: Cache, config: Config, directory: Path
    ) -> t.Optional[t.Tuple[Path, Path]]:
        """Generate a configuration file and a pre-configured binary"""
        platform_binary = cache.platform_binary()
        if not platform_binary:
            LOGGER.critical("unsupported platform!")
            return None
        if system() == 'Linux':
            platform_binary.chmod(0o700)
        # ensure that output directory exists
        directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_config = directory / f'collector-{timestamp}.yml'
        output_binary = (
            directory
            / f'collector-{timestamp}-{self.config.distribution.suffix}'
        )
        # generate collector config file
        LOGGER.info("generating configuration...")
        self.config.generate(cache, config, output_config)
        LOGGER.info("configuration written to: %s", output_config)
        # generate collector binary
        LOGGER.info("generating release binary...")
        template_binary = cache.template_binary(self.config.distribution)
        argv = [
            str(platform_binary),
            'config',
            'repack',
            '--exe',
            str(template_binary),
            str(output_config),
            str(output_binary),
        ]
        LOGGER.info("spawning subprocess: %s", argv)
        run(argv, check=True)
        LOGGER.info("release binary written to: %s", output_binary)
        return output_binary, output_config
