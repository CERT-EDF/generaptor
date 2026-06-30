"""new-profile command module.

This module provides the CLI command for creating new profiles.
"""

from uuid import UUID

from ..concept import Profile
from ..helper.json import dump_json
from ..helper.logging import get_logger

_LOGGER = get_logger('command.new_profile')


def _new_profile_cmd(args):
    """Handle new-profile command execution.

    Args:
        args: Parsed command line arguments with name and targets.
    """
    profile = Profile(name=args.name, targets=set(args.targets))
    print(dump_json(profile.to_dict()))


def setup_cmd(cmd):
    """Setup new-profile command.

    Args:
        cmd: argparse subparsers object to add the command to.
    """
    new_profile = cmd.add_parser('new-profile', help="generate a new profile")
    new_profile.add_argument('name', help="profile name")
    new_profile.add_argument(
        'targets',
        nargs='+',
        type=UUID,
        metavar='target',
        help="profile targets",
    )
    new_profile.set_defaults(func=_new_profile_cmd)
