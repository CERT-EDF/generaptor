"""Target Set API
"""
import typing as t
from json import loads
from pathlib import Path
from dataclasses import dataclass
from .ruleset import RuleSet
from ..helper.csv import stream_csv
from ..helper.prompt import multiselect
from ..helper.logging import LOGGER


@dataclass
class Target:
    """Target"""

    name: str
    rule_uids: t.Set[int]


@dataclass
class TargetSet:
    """Set of targets"""

    targets: t.Mapping[str, Target]

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

    def select(self, rule_set: RuleSet, targets: t.List[str]) -> RuleSet:
        """Build a rule set from an existing ruleset and selected targets"""
        title = "Pick one or more collection targets"
        options = list(sorted(self.targets.keys()))
        if not targets:
            targets = multiselect(title, options)
        rules = {}
        for target in targets:
            target = self.targets[target]
            rules.update(
                {
                    rule_uid: rule_set.rules[rule_uid]
                    for rule_uid in target.rule_uids
                }
            )
            LOGGER.info(
                "select %s (%d rules)", target.name, len(target.rule_uids)
            )
        return RuleSet(rules=rules)
