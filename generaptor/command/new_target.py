"""new-target command"""

from uuid import UUID

from ..concept import Target
from ..helper.json import dump_json
from ..helper.logging import get_logger

_LOGGER = get_logger('command.new_target')


def _new_target_cmd(args):
    target = Target(name=args.name, rules=set(args.rules))
    print(dump_json(target.to_dict()))


def setup_cmd(cmd):
    """Setup new-target command"""
    new_target = cmd.add_parser('new-target', help="generate a new target")
    new_target.add_argument('name', help="target name")
    new_target.add_argument(
        'rules', nargs='+', type=UUID, metavar='rule', help="target rules"
    )
    new_target.set_defaults(func=_new_target_cmd)
