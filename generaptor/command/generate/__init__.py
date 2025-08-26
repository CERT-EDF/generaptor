"""generate command"""

from pathlib import Path

from ...helper.prompt import INTERACTIVE_PROMPT_AVAILABLE
from .linux import setup_target as setup_linux
from .windows import setup_target as setup_windows


def setup_cmd(cmd):
    """Setup generate command"""
    generate = cmd.add_parser('generate', help="generate a collector")
    if INTERACTIVE_PROMPT_AVAILABLE:
        generate.add_argument(
            '--custom',
            '-c',
            action='store_true',
            help="enable collector targets customization (interactive)",
        )
    generate.add_argument(
        '--profile',
        default='default',
        help="use given profile (non-interactive)",
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
    setup_linux(target)
    setup_windows(target)
