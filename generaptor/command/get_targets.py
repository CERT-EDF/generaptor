"""get-targets command module.

This module provides the CLI command for listing available targets
for a specific operating system.
"""

from ..concept import OperatingSystem, get_target_set
from ..helper.json import dump_json
from ..helper.logging import get_logger

_LOGGER = get_logger('command.get_targets')


def _get_targets_cmd(args):
    """Handle get-targets command execution.

    Args:
        args: Parsed command line arguments with opsystem attribute.
    """
    opsystem = OperatingSystem(args.opsystem)
    target_set = get_target_set(args.cache, args.config, opsystem)
    if target_set.empty:
        _LOGGER.warning("empty target set, operation canceled.")
        return
    for target in target_set.values:
        print(dump_json(target.to_dict()))


def setup_cmd(cmd):
    """Setup get-targets command.

    Args:
        cmd: argparse subparsers object to add the command to.
    """
    get_targets = cmd.add_parser(
        'get-targets',
        help="get targets matching operating system",
    )
    get_targets.add_argument(
        'opsystem',
        choices=[item.value for item in OperatingSystem],
        help="Operating system",
    )
    get_targets.set_defaults(func=_get_targets_cmd)
