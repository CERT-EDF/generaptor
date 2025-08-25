"""Generaptor Target Set"""

from dataclasses import dataclass
from json import loads
from pathlib import Path

from ..helper.csv import stream_csv
from ..helper.logging import get_logger
from ..helper.prompt import multiselect
from .ruleset import RuleSet

_LOGGER = get_logger('concept.targetset')


@dataclass
class Target:
    """Target"""

    name: str
    rule_uids: set[int]


@dataclass
class TargetSet:
    """Set of targets"""

    targets: dict[str, Target]

    @property
    def count(self):
        """Count of rules in ruleset"""
        return len(self.targets)

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build ruleset from filepath"""
        targets = {}
        for row in stream_csv(filepath):
            name, rule_uids = row
            targets[name] = Target(name=name, rule_uids=set(loads(rule_uids)))
        return cls(targets=targets)

    def select(self, rule_set: RuleSet, targets: list[str]) -> RuleSet:
        """Build a rule set from an existing ruleset and selected targets"""
        options = list(sorted(self.targets.keys()))
        if not targets:
            targets = multiselect(
                "Pick one or more collection targets", options
            )
        rules = {}
        for name in targets:
            target = self.targets.get(name)
            if not target:
                _LOGGER.warning("skipped unknown target ('%s')", name)
                continue
            rules.update(
                {
                    rule_uid: rule_set.rules[rule_uid]
                    for rule_uid in target.rule_uids
                }
            )
            _LOGGER.info(
                "select %s (%d rules)", target.name, len(target.rule_uids)
            )
        return RuleSet(rules=rules)

    def merge(self, target_set: 'TargetSet', base_uid: int):
        """Merge given target set using given base uid in this target set"""
        for name, target in target_set.targets.items():
            self.targets[name] = Target(
                name=name,
                rule_uids={base_uid + uid for uid in target.rule_uids},
            )
