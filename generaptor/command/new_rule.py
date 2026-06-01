"""new-rule command"""

from ..concept import Rule
from ..helper.json import dump_json
from ..helper.logging import get_logger

_LOGGER = get_logger('command.new_rule')


def _new_rule_cmd(args):
    rule = Rule(
        name=args.name,
        category=args.category,
        glob=args.glob,
        accessor=args.accessor,
        comment=args.comment,
    )
    print(dump_json(rule.to_dict()))


def setup_cmd(cmd):
    """Setup new-rule command"""
    new_rule = cmd.add_parser(
        'new-rule', help="generate a new rule"
    )
    new_rule.add_argument('name', help="rule name")
    new_rule.add_argument('category', help="rule category")
    new_rule.add_argument('glob', help="rule glob pattern")
    new_rule.add_argument('accessor', help="rule accessor")
    new_rule.add_argument('--comment', default='', help="rule comment")
    new_rule.set_defaults(func=_new_rule_cmd)
