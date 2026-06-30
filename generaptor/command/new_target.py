"""new-target command module.

This module provides the CLI command for creating new targets.
"""

from uuid import UUID

from ..concept import Target
from ..helper.json import dump_json
from ..helper.logging import get_logger

_LOGGER = get_logger('command.new_target')


def _new_target_cmd(args):
    """Handle new-target command execution.

    Args:
        args: Parsed command line arguments with name and rules.
    """
    target = Target(name=args.name, rules=set(args.rules))
    print(dump_json(target.to_dict()))


def setup_cmd(cmd):
    """Setup new-target command.

    Args:
        cmd: argparse subparsers object to add the command to.
    """
    new_target = cmd.add_parser('new-target', help="generate a new target")
    new_target.add_argument('name', help="target name")
    new_target.add_argument(
        'rules', nargs='+', type=UUID, metavar='rule', help="target rules"
    )
    new_target.set_defaults(func=_new_target_cmd)
