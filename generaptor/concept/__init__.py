"""Generaptor Concepts"""

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
from .profile import Profile, ProfileMapping
from .ruleset import Rule, RuleSet
from .targetset import Target, TargetSet

_LOGGER = get_logger('concept')


def get_profile_mapping(
    cache: Cache,
    config: Config,
    opsystem: OperatingSystem,
) -> ProfileMapping | None:
    """Load profile mapping for given operating system"""
    # load standard profile mapping
    profile_mapping = cache.config.load_profile_mapping(opsystem)
    # load and merge custom profile mapping
    custom_profile_mapping = config.load_profile_mapping(opsystem)
    if custom_profile_mapping:
        _LOGGER.warning("updating profile mapping...")
        profile_mapping.update(custom_profile_mapping)
    return profile_mapping


def get_rule_set(
    cache: Cache,
    config: Config,
    opsystem: OperatingSystem,
) -> tuple[int | None, RuleSet | None]:
    """Load rule set for given operating system"""
    # load standard rule set
    rule_set = cache.config.load_rule_set(opsystem)
    if not rule_set:
        return None, None
    # load and merge custom rule set
    max_uid = 0
    custom_rule_set = config.load_rule_set(opsystem)
    if custom_rule_set:
        _LOGGER.warning("merging custom rules...")
        max_uid = rule_set.merge(custom_rule_set)
    return max_uid, rule_set


def get_target_set(
    cache: Cache,
    config: Config,
    opsystem: OperatingSystem,
    max_uid: int,
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
        target_set.merge(custom_target_set, max_uid)
    return target_set


def get_ruleset_from_targets(
    cache: Cache,
    config: Config,
    targets: list[str],
    opsystem: OperatingSystem,
) -> RuleSet | None:
    """Load ruleset for given targets and operating system"""
    max_uid, rule_set = get_rule_set(cache, config, opsystem)
    if not rule_set:
        return None
    target_set = get_target_set(cache, config, opsystem, max_uid)
    if not target_set:
        return None
    return target_set.select(rule_set, targets)
