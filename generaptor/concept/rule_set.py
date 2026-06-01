"""Generaptor Rule Set"""

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from uuid import UUID, uuid4

from ..helper.json import load_jsonl
from ..helper.logging import get_logger

_LOGGER = get_logger('concept.ruleset')


@dataclass(kw_only=True, frozen=True)
class Rule:
    """Rule"""

    guid: UUID = field(default_factory=uuid4)
    name: str
    category: str
    glob: str
    accessor: str
    comment: str

    def to_dict(self) -> dict:
        """Convert to dict"""
        dct = asdict(self)
        dct['guid'] = str(dct['guid'])
        return dct


GUIDRuleMapping = dict[UUID, Rule]


@dataclass(kw_only=True)
class RuleSet:
    """Set of rules"""

    by_guid: GUIDRuleMapping

    @property
    def count(self) -> int:
        """Count of rules in ruleset"""
        return len(self.by_guid)

    @property
    def empty(self) -> bool:
        """Determine if ruleset is empty"""
        return not bool(self.by_guid)

    @property
    def values(self) -> Iterable[Rule]:
        """Retrieve values"""
        return self.by_guid.values()

    @classmethod
    def from_iterable(cls, iterable: Iterable[Rule]):
        """Build from iterable"""
        by_guid = {}
        for rule in iterable:
            if rule.guid in by_guid:
                _LOGGER.warning("duplicate rule: %s", rule.guid)
                continue
            by_guid[rule.guid] = rule
        return cls(by_guid=by_guid)

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build from filepath"""
        return cls.from_iterable(
            Rule(
                guid=UUID(row['guid']),
                name=row['name'],
                category=row['category'],
                glob=row['glob'],
                accessor=row['accessor'],
                comment=row['comment'],
            )
            for row in load_jsonl(filepath)
        )

    def merge(self, rule_set: 'RuleSet') -> bool:
        """Merge rules from given rule set in this rule set"""
        guids = set(self.by_guid)
        duplicates = guids.intersection(set(rule_set.by_guid))
        if duplicates:
            _LOGGER.warning("failed to merge, duplicate rules: %s", duplicates)
            return False
        self.by_guid.update(rule_set.by_guid)
        return True
