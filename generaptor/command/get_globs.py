"""get-globs command"""

from json import dumps

from ..concept import (
    OperatingSystem,
    get_profile_mapping,
    get_ruleset_from_targets,
)
from ..helper.logging import get_logger

_LOGGER = get_logger('command.get_globs')


def _get_globs_cmd(args):
    opsystem = OperatingSystem(args.opsystem)
    profile_mapping = get_profile_mapping(args.cache, args.config, opsystem)
    profile = profile_mapping.get(args.profile)
    if profile:
        args.targets += profile.targets
    try:
        rule_set = get_ruleset_from_targets(
            args.cache, args.config, args.targets, opsystem
        )
    except KeyboardInterrupt:
        print()
        _LOGGER.warning("operation canceled.")
        return
    if rule_set.empty:
        _LOGGER.warning("empty rule set, operation canceled.")
        return
    for rule in rule_set.rules.values():
        print(
            dumps(
                {'uid': rule.uid, 'accessor': rule.accessor, 'glob': rule.glob}
            )
        )


def setup_cmd(cmd):
    """Setup get-globs command"""
    get_globs = cmd.add_parser(
        'get-globs',
        help="get globs matching collection targets",
    )
    get_globs.add_argument(
        '--profile',
        help="use given profile (non-interactive)",
    )
    get_globs.add_argument(
        '--targets',
        metavar='target',
        default=[],
        nargs='+',
        help="collection targets",
    )
    get_globs.add_argument(
        'opsystem',
        choices=[item.value for item in OperatingSystem],
        help="Operating system",
    )
    get_globs.set_defaults(func=_get_globs_cmd)
