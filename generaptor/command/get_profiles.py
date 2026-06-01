"""get-profiles command"""

from ..concept import OperatingSystem, get_profile_set
from ..helper.json import dump_json
from ..helper.logging import get_logger

_LOGGER = get_logger('command.get_profiles')


def _get_profiles_cmd(args):
    opsystem = OperatingSystem(args.opsystem)
    profile_set = get_profile_set(args.cache, args.config, opsystem)
    if profile_set.empty:
        _LOGGER.warning("empty profile set, operation canceled.")
        return
    for profile in profile_set.values:
        print(dump_json(profile.to_dict()))



def setup_cmd(cmd):
    """Setup get-profiles command"""
    get_profiles = cmd.add_parser(
        'get-profiles',
        help="get profiles matching operating system",
    )
    get_profiles.add_argument(
        'opsystem',
        choices=[item.value for item in OperatingSystem],
        help="Operating system",
    )
    get_profiles.set_defaults(func=_get_profiles_cmd)
