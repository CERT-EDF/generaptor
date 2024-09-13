"""Generaptor API
"""

from typing import Optional
from .cache import Cache
from .collection import Collection, CollectionList
from .collector import CollectorConfig, Collector
from .config import Config
from .custom_profile import CustomProfile
from .distribution import (
    SUPPORTED_DISTRIBUTIONS,
    DEFAULT_OS_TARGETS_MAPPING,
    Distribution,
    OperatingSystem,
    Architecture,
)
from .ruleset import RuleSet, Rule
from .targetset import TargetSet, Target
from ..helper.logging import LOGGER


def ruleset_from_targets(
    cache: Cache,
    config: Config,
    targets: list[str],
    operating_system: OperatingSystem,
) -> Optional[RuleSet]:
    """Load ruleset for given targets and operating system"""
    # load standard ruleset and targetset from cache
    rule_set = cache.load_rule_set(operating_system)
    if not rule_set:
        return None
    target_set = cache.load_target_set(operating_system)
    if not target_set:
        return None
    # load and merge custom ruleset and targetset from config if available
    custom_rule_set = config.load_rule_set(operating_system)
    if custom_rule_set:
        LOGGER.warning("merging custom rules...")
        max_uid = rule_set.merge(custom_rule_set)
    custom_target_set = config.load_target_set(operating_system)
    if custom_target_set:
        LOGGER.warning("merging custom targets...")
        target_set.merge(custom_target_set, max_uid)
    return target_set.select(rule_set, targets)
