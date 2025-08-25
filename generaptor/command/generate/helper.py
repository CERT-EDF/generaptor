"""Generate command helper"""

from ...concept import OperatingSystem, get_profile_mapping
from ...helper.logging import get_logger

_LOGGER = get_logger('command.generate.helper')


class ProfileNotFoundError(Exception):
    """Raised when profile cannot be found"""


def select_targets(args, opsystem: OperatingSystem):
    """Select targets for given operating system"""
    if getattr(args, 'custom', False):
        return []
    _LOGGER.info("using profile: %s", args.profile)
    profile_mapping = get_profile_mapping(args.cache, args.config, opsystem)
    profile = profile_mapping.get(args.profile)
    if not profile:
        raise ProfileNotFoundError
    return profile.targets
