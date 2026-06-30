"""Command module.

This module provides all CLI command implementations for generaptor.
Each submodule contains a specific command and its setup function.
"""

from .extract import setup_cmd as setup_extract
from .generate import setup_cmd as setup_generate
from .get_fingerprint import setup_cmd as setup_get_fingerprint
from .get_metadata import setup_cmd as setup_get_metadata
from .get_profiles import setup_cmd as setup_get_profiles
from .get_rules import setup_cmd as setup_get_rules
from .get_secret import setup_cmd as setup_get_secret
from .get_targets import setup_cmd as setup_get_targets
from .new_profile import setup_cmd as setup_new_profile
from .new_rule import setup_cmd as setup_new_rule
from .new_target import setup_cmd as setup_new_target
from .update import setup_cmd as setup_update


def setup_commands(cmd):
    """Setup all available commands.

    Args:
        cmd: argparse subparsers object to which commands will be added.
    """
    setup_update(cmd)
    setup_get_rules(cmd)
    setup_get_targets(cmd)
    setup_get_profiles(cmd)
    setup_new_rule(cmd)
    setup_new_target(cmd)
    setup_new_profile(cmd)
    setup_generate(cmd)
    setup_extract(cmd)
    setup_get_secret(cmd)
    setup_get_metadata(cmd)
    setup_get_fingerprint(cmd)
