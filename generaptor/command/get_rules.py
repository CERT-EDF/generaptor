"""get-rules command"""

from ..concept import (
    OperatingSystem,
    get_profile_set,
    get_rule_set,
    get_rule_set_from_targets,
)
from ..helper.json import dump_json
from ..helper.logging import get_logger

_LOGGER = get_logger('command.get_rules')


def _get_rules_cmd(args):
    opsystem = OperatingSystem(args.opsystem)
    if args.profile:
        profile_set = get_profile_set(args.cache, args.config, opsystem)
        profile = profile_set.by_name.get(args.profile)
        rule_set = get_rule_set_from_targets(
            args.cache, args.config, opsystem, profile.targets
        )
    elif args.targets:
        rule_set = get_rule_set_from_targets(
            args.cache, args.config, opsystem, args.targets
        )
    else:
        rule_set = get_rule_set(args.cache, args.config, opsystem)
    if rule_set.empty:
        _LOGGER.warning("empty rule set, operation canceled.")
        return
    for rule in rule_set.values:
        print(dump_json(rule.to_dict()))


def setup_cmd(cmd):
    """Setup get-rules command"""
    get_rules = cmd.add_parser(
        'get-rules',
        help="get rules matching collection targets",
    )
    get_rules.add_argument(
        'opsystem',
        choices=[item.value for item in OperatingSystem],
        help="Operating system",
    )
    group = get_rules.add_mutually_exclusive_group()
    group.add_argument(
        '--profile',
        help="use given profile (non-interactive)",
    )
    group.add_argument(
        '--targets',
        metavar='target',
        default=[],
        nargs='+',
        help="collection targets",
    )
    get_rules.set_defaults(func=_get_rules_cmd)
