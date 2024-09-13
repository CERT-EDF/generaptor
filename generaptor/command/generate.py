"""generate command
"""

from pathlib import Path
from ..api import (
    DEFAULT_OS_TARGETS_MAPPING,
    Collector,
    Distribution,
    Architecture,
    CustomProfile,
    CollectorConfig,
    OperatingSystem,
    ruleset_from_targets,
)
from ..helper.crypto import provide_x509_certificate
from ..helper.logging import LOGGER
from ..helper.validation import check_device


def _select_targets(args, operating_system: OperatingSystem):
    default = DEFAULT_OS_TARGETS_MAPPING[operating_system]
    if args.custom:
        return []
    if args.custom_profile and args.custom_profile.is_file():
        custom_profile = CustomProfile.from_filepath(args.custom_profile)
        if custom_profile.targets:
            return custom_profile.targets
    return default


def _generate_linux_cmd(args):
    LOGGER.info("starting linux collector generator...")
    if not check_device(args.device):
        return
    distribution = Distribution(
        operating_system=OperatingSystem.LINUX,
        architecture=Architecture(args.architecture),
    )
    targets = _select_targets(args, distribution.operating_system)
    try:
        rule_set = ruleset_from_targets(
            args.cache, args.config, targets, distribution.operating_system
        )
        if rule_set.empty:
            LOGGER.warning("empty rule set, operation canceled.")
            return
        certificate = provide_x509_certificate(
            args.output_directory,
            args.x509_certificate,
            args.ask_password,
        )
    except KeyboardInterrupt:
        print()
        LOGGER.warning("operation canceled.")
        return
    config = CollectorConfig(
        device=args.device,
        rule_set=rule_set,
        certificate=certificate,
        distribution=distribution,
    )
    collector = Collector(config=config)
    collector.generate(args.cache, args.config, args.output_directory)


def _generate_windows_cmd(args):
    LOGGER.info("starting windows collector generator...")
    if not check_device(args.device):
        return
    if args.device and not args.device.endswith(':'):
        LOGGER.warning("assuming device name is '%s:'", args.device)
        args.device += ':'
    distribution = Distribution(
        operating_system=OperatingSystem.WINDOWS,
        architecture=Architecture(args.architecture),
    )
    targets = _select_targets(args, distribution.operating_system)
    try:
        rule_set = ruleset_from_targets(
            args.cache, args.config, targets, distribution.operating_system
        )
        if rule_set.empty:
            LOGGER.warning("empty rule set, operation canceled.")
            return
        certificate = provide_x509_certificate(
            args.output_directory,
            args.x509_certificate,
            args.ask_password,
        )
    except KeyboardInterrupt:
        print()
        LOGGER.warning("operation canceled.")
        return
    config = CollectorConfig(
        device=args.device,
        rule_set=rule_set,
        certificate=certificate,
        distribution=distribution,
        dont_be_lazy=args.dont_be_lazy,
        vss_analysis_age=args.vss_analysis_age,
        use_auto_accessor=(not args.no_auto_accessor),
    )
    collector = Collector(config=config)
    collector.generate(args.cache, args.config, args.output_directory)


def setup_cmd(cmd):
    """Setup generate command"""
    generate = cmd.add_parser('generate', help="generate a collector")
    generate.add_argument(
        '--custom',
        '-c',
        action='store_true',
        help="enable collector targets customization (interactive)",
    )
    generate.add_argument(
        '--custom-profile',
        '--cp',
        type=Path,
        help="use given customization profile (non interactive)",
    )
    generate.add_argument(
        '--output-directory',
        '-o',
        type=Path,
        default=Path('output').resolve(),
        help="set output directory",
    )
    generate.add_argument(
        '--x509-certificate',
        '-x',
        type=Path,
        help="bring your own x509 certificate instead of generating one "
        "(must be RSA)",
    )
    generate.add_argument(
        '--ask-password',
        '-p',
        action='store_true',
        help="prompt for private key password instead of generating one or "
        "reading GENERAPTOR_PK_SECRET environment variable (ignored if "
        "--x509 is used)",
    )
    target = generate.add_subparsers(dest='target')
    target.required = True
    linux = target.add_parser('linux', help="generate linux collector")
    linux.set_defaults(func=_generate_linux_cmd)
    linux.add_argument(
        '--architecture',
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
    windows = target.add_parser('windows', help="Generate windows collector")
    windows.set_defaults(func=_generate_windows_cmd)
    windows.add_argument(
        '--architecture',
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
        '--no-auto-accessor',
        action='store_true',
        help="disable auto accessor (which automatically select fastest collection technique)",
    )
    windows.add_argument(
        '--vss-analysis-age',
        type=int,
        default=0,
        help="analyze VSS within this many days ago, 0 means no VSS analysis",
    )
    windows.add_argument(
        '--dont-be-lazy',
        action='store_true',
        help="disable lazy_ntfs accessor (which uses OS api calls to collect files)",
    )
