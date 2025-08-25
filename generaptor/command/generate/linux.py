"""Generate linux target"""

from ...concept import (
    Architecture,
    Collector,
    CollectorConfig,
    Distribution,
    OperatingSystem,
    get_ruleset_from_targets,
)
from ...helper.crypto import provide_x509_certificate
from ...helper.logging import get_logger
from ...helper.validation import check_device
from .helper import ProfileNotFoundError, select_targets

_LOGGER = get_logger('command.generate.linux')


def _generate_linux_cmd(args):
    _LOGGER.info("starting linux collector generator...")
    if not check_device(args.device):
        return
    distribution = Distribution(
        arch=Architecture(args.arch),
        opsystem=OperatingSystem.LINUX,
    )
    try:
        targets = select_targets(args, distribution.opsystem)
    except ProfileNotFoundError:
        _LOGGER.error("cannot find profile: %s", args.profile)
        return
    try:
        rule_set = get_ruleset_from_targets(
            args.cache, args.config, targets, distribution.opsystem
        )
        if rule_set.empty:
            _LOGGER.warning("empty rule set, operation canceled.")
            return
        certificate = provide_x509_certificate(
            args.output_directory,
            args.x509_certificate,
            args.ask_password,
        )
    except KeyboardInterrupt:
        print()
        _LOGGER.warning("operation canceled.")
        return
    config = CollectorConfig(
        device=args.device,
        rule_set=rule_set,
        certificate=certificate,
        distribution=distribution,
    )
    collector = Collector(config=config)
    collector.generate(args.cache, args.config, args.output_directory)


def setup_target(target):
    """Setup linux target"""
    linux = target.add_parser('linux', help="generate linux collector")
    linux.set_defaults(func=_generate_linux_cmd)
    linux.add_argument(
        '--arch',
        '-a',
        default=Architecture.AMD64.value,
        choices=[arch.value for arch in Architecture],
        help="set released binary architecture",
    )
    linux.add_argument(
        '--device',
        '-d',
        default='',
        help="set root directory (absolute path), empty means '/'",
    )
