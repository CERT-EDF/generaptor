"""Rule Set API
"""
import typing as t
from pathlib import Path
from dataclasses import dataclass
from ..helper.csv import stream_csv
from ..helper.logging import LOGGER


@dataclass
class Rule:
    """Rule"""

    uid: int
    name: str
    category: str
    glob: str
    accessor: str
    comment: str


@dataclass
class RuleSet:
    """Set of rules"""

    rules: t.Mapping[int, Rule]

    @property
    def count(self) -> int:
        """Count of rules in ruleset"""
        return len(self.rules)

    @property
    def max_uid(self) -> int:
        """Max uid"""
        return max(self.rules.keys())

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build ruleset from filepath"""
        rules = {}
        for row in stream_csv(filepath):
            try:
                uid, name, category, glob, accessor, comment = row
            except ValueError:
                LOGGER.warning("skipped invalid ruleset row: %s", row)
                continue
            rules[int(uid)] = Rule(
                uid=int(uid),
                name=name,
                category=category,
                glob=glob,
                accessor=accessor,
                comment=comment,
            )
        return cls(rules=rules)

    def merge(self, rule_set: 'RuleSet') -> int:
        """Merge rules from given rule set in this rule set"""
        base_uid = self.max_uid
        for uid, rule in rule_set.rules.items():
            rule.uid = base_uid + uid
            self.rules[rule.uid] = rule
        return base_uid
