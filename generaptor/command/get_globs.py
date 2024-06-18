"""get-globs command
"""
from pathlib import Path
from rich.box import ROUNDED
from rich.table import Table
from rich.console import Console
from ..api import OperatingSystem, ruleset_from_targets
from ..helper.logging import LOGGER


def _get_globs_cmd(args):
    try:
        rule_set = ruleset_from_targets(
            args.cache,
            args.config,
            args.targets,
            OperatingSystem(args.operating_system),
        )
    except KeyboardInterrupt:
        print()
        LOGGER.warning("operation canceled.")
        return
    if not rule_set:
        LOGGER.warning("empty rule set, operation canceled.")
        return
    table = Table(
        "UID",
        "Accessor",
        "Glob",
        box=ROUNDED,
        expand=True,
        highlight=False,
        row_styles=['', 'dim'],
        show_header=False,
    )
    for rule in rule_set.rules.values():
        table.add_row(str(rule.uid), rule.accessor, rule.glob)
    console = Console()
    console.print(table)

def setup_cmd(cmd):
    """Setup get-globs command"""
    get_globs = cmd.add_parser(
        'get-globs',
        help="get globs matching collection targets",
    )
    get_globs.add_argument(
        '--targets',
        metavar='target',
        default=[],
        nargs='+',
        type=Path,
        help="collection targets",
    )
    get_globs.add_argument(
        'operating_system',
        choices=[item.value for item in OperatingSystem],
        help="Operating system",
    )
    get_globs.set_defaults(func=_get_globs_cmd)
