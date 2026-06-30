"""Generaptor Collector module.

This module provides functionality for generating Velociraptor collectors,
including collector configuration and binary generation.
"""

from csv import QUOTE_MINIMAL, writer
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from pathlib import Path
from platform import system
from subprocess import CalledProcessError, run

from ..__version__ import version
from ..helper.crypto import Certificate, fingerprint, pem_string
from ..helper.logging import get_logger
from .cache import Cache
from .config import Config
from .distribution import Distribution, OperatingSystem
from .rule_set import RuleSet

_LOGGER = get_logger('concept.collector')


def _globs_from_ruleset(rule_set: RuleSet):
    """Generate CSV glob patterns from rule set.

    Args:
        rule_set (RuleSet): The rule set to generate glob patterns from.

    Returns:
        str: CSV-formatted string containing glob and accessor pairs.
    """
    imstr = StringIO()
    csv_writer = writer(
        imstr, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL
    )
    for rule in rule_set.values:
        csv_writer.writerow([rule.glob, rule.accessor])
    file_globs = imstr.getvalue()
    imstr.close()
    return file_globs


@dataclass
class CollectorConfig:
    """Collector configuration.

    Configuration for generating a Velociraptor collector.

    Attributes:
        device (str): Device name/identifier for the collector.
        rule_set (RuleSet): Set of rules to include in the collector.
        certificate (Certificate): TLS certificate for the collector.
        distribution (Distribution): Target distribution (OS + architecture).
        memdump (bool): Whether to enable memory dumping (Windows only).
        dont_be_lazy (bool | None): Whether to disable lazy collection (Windows only).
        vss_analysis_age (int | None): VSS analysis age in days (Windows only).
        use_auto_accessor (bool | None): Whether to use automatic accessor (Windows only).
    """

    device: str
    rule_set: RuleSet
    certificate: Certificate
    distribution: Distribution
    memdump: bool = False
    dont_be_lazy: bool | None = None
    vss_analysis_age: int | None = None
    use_auto_accessor: bool | None = None

    @property
    def context(self):
        """Context for jinja template engine.

        Returns:
            dict: Context dictionary used for template rendering,
                 including version, device, certificate data, and file globs.
        """
        ctx = {
            'version': version,
            'device': self.device,
            'cert_data_pem_str': pem_string(self.certificate),
            'cert_fingerprint_hex': fingerprint(self.certificate),
            'file_globs': _globs_from_ruleset(self.rule_set),
        }
        if self.distribution.opsystem == OperatingSystem.WINDOWS:
            ctx.update(
                {
                    'memdump': self.memdump,
                    'dont_be_lazy': 'Y' if self.dont_be_lazy else 'N',
                    'vss_analysis_age': self.vss_analysis_age,
                    'use_auto_accessor': (
                        'Y' if self.use_auto_accessor else 'N'
                    ),
                }
            )
        return ctx

    def generate(self, cache: Cache, config: Config, filepath: Path):
        """Generate configuration file data.

        Args:
            cache (Cache): Cache instance for standard template fallback.
            config (Config): Config instance for custom template lookup.
            filepath (Path): Output path for the generated configuration file.
        """
        vql_template = config.vql_template(self.distribution.opsystem)
        if vql_template is None:
            vql_template = cache.config.vql_template(
                self.distribution.opsystem
            )
        else:
            _LOGGER.warning("using custom VQL template...")
        with filepath.open('wb') as fstream:
            stream = vql_template.stream(self.context)
            stream.dump(fstream, encoding='utf-8')


@dataclass
class Collector:
    """Collector.

    Represents a Velociraptor collector with its configuration.

    Attributes:
        config (CollectorConfig): Configuration for this collector.
    """

    config: CollectorConfig

    def generate(
        self, cache: Cache, config: Config, directory: Path
    ) -> tuple[Path, Path] | None:
        """Generate a configuration file and a pre-configured binary.

        Args:
            cache (Cache): Cache instance for binary and template access.
            config (Config): Config instance for custom template lookup.
            directory (Path): Output directory for generated files.

        Returns:
            tuple[Path, Path] | None: Tuple of (binary_path, config_path) if successful,
                                 None if generation failed.
        """
        platform_binary = cache.platform_binary()
        if not platform_binary:
            _LOGGER.critical("unsupported platform!")
            return None
        if system() in {'Linux', 'Darwin'}:
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
        _LOGGER.info("generating configuration...")
        self.config.generate(cache, config, output_config)
        _LOGGER.info("configuration written to: %s", output_config)
        # generate collector binary
        _LOGGER.info("generating release binary...")
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
        _LOGGER.info("spawning subprocess: %s", argv)
        try:
            run(argv, check=True)
        except CalledProcessError as exc:
            _LOGGER.critical("repack failed (exit %d)", exc.returncode)
            output_config.unlink(missing_ok=True)
            return None
        _LOGGER.info("release binary written to: %s", output_binary)
        return output_binary, output_config
