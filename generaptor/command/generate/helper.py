"""Generate command helper"""

from ...concept import OperatingSystem, get_profile_set
from ...helper.logging import get_logger

_LOGGER = get_logger('command.generate.helper')


class ProfileNotFoundError(Exception):
    """Raised when profile cannot be found"""


def select_targets(args, opsystem: OperatingSystem):
    """Select targets for given operating system"""
    if getattr(args, 'custom', False):
        return []
    _LOGGER.info("using profile: %s", args.profile)
    profile_set = get_profile_set(args.cache, args.config, opsystem)
    profile = profile_set.by_name.get(args.profile)
    if not profile:
        raise ProfileNotFoundError
    return profile.targets
