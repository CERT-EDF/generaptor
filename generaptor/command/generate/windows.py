"""Generate windows target module.

This module provides the Windows-specific collector generation command.
"""

from ...concept import (
    Architecture,
    Collector,
    CollectorConfig,
    Distribution,
    OperatingSystem,
    get_rule_set_from_targets,
)
from ...helper.crypto import provide_x509_certificate
from ...helper.logging import get_logger
from ...helper.validation import check_device
from .helper import ProfileNotFoundError, select_targets

_LOGGER = get_logger('command.generate.windows')


def _generate_windows_cmd(args):
    """Handle Windows collector generation command.

    Args:
        args: Parsed command line arguments for Windows collector generation.
    """
    _LOGGER.info("starting windows collector generator...")
    if not check_device(args.device):
        return
    if args.device and not args.device.endswith(':'):
        _LOGGER.warning("assuming device name is '%s:'", args.device)
        args.device += ':'
    distribution = Distribution(
        arch=Architecture(args.arch),
        opsystem=OperatingSystem.WINDOWS,
    )
    try:
        targets = select_targets(args, distribution.opsystem)
    except ProfileNotFoundError:
        _LOGGER.error("cannot find profile: %s", args.profile)
        return
    try:
        rule_set = get_rule_set_from_targets(
            args.cache, args.config, distribution.opsystem, targets
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
        memdump=args.memdump,
        dont_be_lazy=args.dont_be_lazy,
        vss_analysis_age=args.vss_analysis_age,
        use_auto_accessor=(not args.no_auto_accessor),
    )
    collector = Collector(config=config)
    collector.generate(args.cache, args.config, args.output_directory)


def setup_target(target):
    """Setup windows target.

    Args:
        target: argparse subparsers object to add the Windows target command to.
    """
    windows = target.add_parser('windows', help="Generate windows collector")
    windows.set_defaults(func=_generate_windows_cmd)
    windows.add_argument(
        '--arch',
        '-a',
        default=Architecture.AMD64.value,
        choices=[arch.value for arch in Architecture],
        help="set released binary architecture",
    )
    windows.add_argument(
        '--device',
        '-d',
        default='',
        help="set root directory (absolute path), empty means all filesystems",
    )
    windows.add_argument(
        '--memdump',
        action='store_true',
        help="Perform and collect physical memory dump",
    )
    windows.add_argument(
        '--no-auto-accessor',
        action='store_true',
        help="disable auto accessor (which automatically select fastest collection technique)",
    )
    windows.add_argument(
        '--vss-analysis-age',
        type=int,
        default=0,
        metavar='N',
        help="analyze VSS within N days ago, 0 means no VSS analysis",
    )
    windows.add_argument(
        '--dont-be-lazy',
        action='store_true',
        help="disable lazy_ntfs accessor (which uses OS api calls to collect files)",
    )
