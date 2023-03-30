"""Generation
"""
from io import StringIO
from csv import writer, QUOTE_MINIMAL
from pathlib import Path
from platform import system
from datetime import datetime
from subprocess import run
from .cache import Cache
from .crypto import Certificate, fingerprint, pem_string
from .prompt import multiselect
from .logging import LOGGER
from .distrib import Distribution


def _dump_file_globs(selected_rules):
    imstr = StringIO()
    csv_writer = writer(
        imstr, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL
    )
    for rule in selected_rules:
        csv_writer.writerow(rule[2:4])
    file_globs = imstr.getvalue()
    imstr.close()
    return file_globs


class Generator:
    """Generate configuration file and velociraptor pre-configured binary"""

    def __init__(
        self,
        distrib: Distribution,
        cache: Cache,
        certificate: Certificate,
        output_directory: Path,
    ):
        self._distrib = distrib
        self._cache = cache
        self._certificate = certificate
        self._output_directory = output_directory

    def _select_globs(self, default_targets=None):
        rules = self._cache.load_rules(self._distrib)
        targets = self._cache.load_targets(self._distrib)
        title = "Pick one or more collection targets"
        options = list(sorted(targets.keys()))
        selected_targets = default_targets
        if not selected_targets:
            selected_targets = multiselect(title, options)
        selected_indices = set()
        LOGGER.info("generating for targets:")
        for target in selected_targets:
            indices = targets[target]
            LOGGER.info(" * %s (%d rules)", target, len(indices))
            selected_indices.update(indices)
        return _dump_file_globs(rules[index] for index in selected_indices)

    def _generate_config(self, context, output_config):
        with output_config.open('wb') as fstream:
            template = self._cache.template_config(self._distrib)
            stream = template.stream(context)
            stream.dump(fstream, encoding='utf-8')

    def generate(self, context, default_targets=None):
        """Generate a configuration file and a pre-configured binary"""
        # check platform binary availability
        platform_binary = self._cache.platform_binary()
        if not platform_binary:
            LOGGER.critical("unsupported platform!")
            return
        if system() == 'Linux':
            platform_binary.chmod(0o700)
        try:
            file_globs = self._select_globs(default_targets)
        except KeyboardInterrupt:
            LOGGER.warning("operation canceled by user.")
            return
        context.update(
            {
                'cert_data_pem_str': pem_string(self._certificate),
                'cert_fingerprint_hex': fingerprint(self._certificate),
                'file_globs': file_globs,
            }
        )
        self._output_directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_config = self._output_directory / f'collector-{timestamp}.yml'
        output_binary = (
            self._output_directory
            / f'collector-{timestamp}-{self._distrib.suffix}'
        )
        template_binary = self._cache.template_binary(self._distrib)
        LOGGER.info("generating configuration...")
        self._generate_config(context, output_config)
        LOGGER.info("configuration written to: %s", output_config)
        LOGGER.info("generating release binary...")
        args = [
            str(platform_binary),
            'config',
            'repack',
            '--exe',
            str(template_binary),
            str(output_config),
            str(output_binary),
        ]
        LOGGER.info("running command: %s", args)
        run(args, check=True)
        LOGGER.info("release binary written to: %s", output_binary)
