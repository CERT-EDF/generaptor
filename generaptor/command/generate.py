"""generate command
"""
from json import loads
from pathlib import Path
from ..helper.crypto import provide_x509_certificate
from ..helper.logging import LOGGER
from ..helper.distrib import Distribution, Architecture, OperatingSystem
from ..helper.validation import check_device
from ..helper.generation import Generator


def _load_custom_profile_targets(custom_profile):
    try:
        custom_profile = loads(custom_profile.read_text())
        return custom_profile.get('targets')
    except:
        LOGGER.exception("failed to load custom profile!")
    return None


def _select_default_targets(args, default_targets):
    if args.custom:
        return None
    if args.custom_profile and args.custom_profile.is_file():
        targets = _load_custom_profile_targets(args.custom_profile)
        if not targets:
            LOGGER.warning(
                "failed to load custom profile, using default targets instead."
            )
            return default_targets
        return targets
    return default_targets


def _generate_linux_cmd(args):
    LOGGER.info("starting linux collector generator...")
    default_targets = _select_default_targets(args, ['LinuxTriage'])
    if not check_device(args.device):
        return
    try:
        certificate = provide_x509_certificate(
            args.output_directory,
            args.x509_certificate,
            args.ask_password,
        )
    except KeyboardInterrupt:
        print()
        LOGGER.warning("operation canceled.")
        return
    artifacts = ['Linux.Collector']
    if args.extra:
        artifacts += [
            'Linux.Mounts',
            'Linux.Ssh.KnownHosts',
            'Linux.Ssh.AuthorizedKeys',
            'Linux.Sys.Users',
            'Linux.Sys.Pslist',
            'Linux.Sys.Crontab',
            'Linux.Sys.LastUserLogin',
            'Linux.Proc.Arp',
            'Linux.Proc.Modules',
            'Linux.Syslog.SSHLogin',
            'Linux.Network.Netstat',
        ]
    Generator(
        Distribution(OperatingSystem.LINUX, Architecture(args.architecture)),
        args.cache,
        certificate,
        args.output_directory,
    ).generate(
        {
            'device': args.device,
            'artifacts': ','.join([f'"{artifact}"' for artifact in artifacts]),
        },
        default_targets,
    )


def _generate_windows_cmd(args):
    LOGGER.info("starting windows collector generator...")
    default_targets = _select_default_targets(args, ['KapeTriage'])
    if not check_device(args.device):
        return
    if args.device and not args.device.endswith(':'):
        LOGGER.warning("assuming device name is '%s:'", args.device)
        args.device += ':'
    try:
        certificate = provide_x509_certificate(
            args.output_directory,
            args.x509_certificate,
            args.ask_password,
        )
    except KeyboardInterrupt:
        print()
        LOGGER.warning("operation canceled.")
        return
    artifacts = ['Windows.Collector']
    if args.extra:
        artifacts += [
            'Windows.Sys.Users',
            'Windows.Packs.Persistence',
            'Windows.System.Pslist',
            'Windows.Network.ArpCache',
            'Windows.Network.NetstatEnriched',
            'Windows.Network.InterfaceAddresses',
        ]
    Generator(
        Distribution(OperatingSystem.WINDOWS, Architecture(args.architecture)),
        args.cache,
        certificate,
        args.output_directory,
    ).generate(
        {
            'device': args.device,
            'artifacts': ','.join([f'"{artifact}"' for artifact in artifacts]),
            'use_auto_accessor': 'N' if args.no_auto_accessor else 'Y',
            'vss_analysis': 'N' if args.no_vss_analysis else 'Y',
            'dont_be_lazy': 'Y' if args.dont_be_lazy else 'N',
        },
        default_targets,
    )


def setup_generate(cmd):
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
        '--extra',
        '-e',
        action='store_true',
        help="run extra collectors depending on targeted platform",
    )
    generate.add_argument(
        '--output-directory',
        '-o',
        type=Path,
        default=Path('output').resolve(),
        help="set output folder",
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
        '--no-vss-analysis',
        action='store_true',
        help="disable windows volume shadow copies analysis",
    )
    windows.add_argument(
        '--dont-be-lazy',
        action='store_true',
        help="disable lazy_ntfs accessor (which uses OS api calls to collect files)",
    )
