"""Generate command helper module.

This module provides helper functionality for the generate command,
including target selection and profile handling.
"""

from ...concept import OperatingSystem, get_profile_set
from ...helper.logging import get_logger

_LOGGER = get_logger('command.generate.helper')


class ProfileNotFoundError(Exception):
    """Raised when profile cannot be found.

    Exception raised when a specified profile is not found in the profile set.
    """


def select_targets(args, opsystem: OperatingSystem):
    """Select targets for given operating system.

    Args:
        args: Parsed command line arguments with profile selection settings.
        opsystem (OperatingSystem): Target operating system.

    Returns:
        list: List of target GUIDs from the selected profile, or empty list for custom selection.

    Raises:
        ProfileNotFoundError: If the specified profile cannot be found.
    """
    if getattr(args, 'custom', False):
        return []
    _LOGGER.info("using profile: %s", args.profile)
    profile_set = get_profile_set(args.cache, args.config, opsystem)
    profile = profile_set.by_name.get(args.profile)
    if not profile:
        raise ProfileNotFoundError
    return profile.targets
