"""Generaptor Concepts"""

from uuid import UUID

from ..helper.logging import get_logger
from .cache import Cache
from .collection import Collection, CollectionList, Outcome
from .collector import Collector, CollectorConfig
from .config import Config
from .distribution import (
    SUPPORTED_DISTRIBUTIONS,
    Architecture,
    Distribution,
    OperatingSystem,
)
from .profile_set import (
    GUIDProfileMapping,
    NameProfileMapping,
    Profile,
    ProfileSet,
)
from .rule_set import GUIDRuleMapping, Rule, RuleSet
from .target_set import GUIDTargetMapping, NameTargetMapping, Target, TargetSet

_LOGGER = get_logger('concept')


def get_profile_set(
    cache: Cache,
    config: Config,
    opsystem: OperatingSystem,
) -> ProfileSet | None:
    """Load profile mapping for given operating system"""
    # load standard profile mapping
    profile_set = cache.config.load_profile_set(opsystem)
    # load and merge custom profile mapping
    custom_profile_set = config.load_profile_set(opsystem)
    if custom_profile_set:
        _LOGGER.warning("merging custom profiles...")
        profile_set.merge(custom_profile_set)
    return profile_set


def get_rule_set(
    cache: Cache,
    config: Config,
    opsystem: OperatingSystem,
) -> RuleSet | None:
    """Load rule set for given operating system"""
    # load standard rule set
    rule_set = cache.config.load_rule_set(opsystem)
    if not rule_set:
        return None
    # load and merge custom rule set
    custom_rule_set = config.load_rule_set(opsystem)
    if custom_rule_set:
        _LOGGER.warning("merging custom rules...")
        rule_set.merge(custom_rule_set)
    return rule_set


def get_target_set(
    cache: Cache,
    config: Config,
    opsystem: OperatingSystem,
) -> TargetSet | None:
    """Load target set for given operating system"""
    # load standard target set
    target_set = cache.config.load_target_set(opsystem)
    if not target_set:
        return None
    # load and merge custom target set
    custom_target_set = config.load_target_set(opsystem)
    if custom_target_set:
        _LOGGER.warning("merging custom targets...")
        target_set.merge(custom_target_set)
    return target_set


def get_rule_set_from_targets(
    cache: Cache,
    config: Config,
    opsystem: OperatingSystem,
    targets: list[str | UUID],
) -> RuleSet | None:
    """Load ruleset for given targets and operating system"""
    rule_set = get_rule_set(cache, config, opsystem)
    if not rule_set:
        return None
    target_set = get_target_set(cache, config, opsystem)
    if not target_set:
        return None
    return target_set.select(rule_set, targets)
