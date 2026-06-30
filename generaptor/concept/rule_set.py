"""Generaptor Rule Set module.

This module provides data structures for managing rules in generaptor,
including the Rule class and RuleSet collection.
"""

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from uuid import UUID, uuid4

from ..helper.json import load_jsonl
from ..helper.logging import get_logger

_LOGGER = get_logger('concept.ruleset')


@dataclass(kw_only=True, frozen=True)
class Rule:
    """Rule.

    Represents a single Velociraptor rule with metadata for artifact collection.

    Attributes:
        guid (UUID): Unique identifier for the rule.
        name (str): Human-readable name of the rule.
        category (str): Category to which this rule belongs.
        glob (str): Glob pattern for file matching.
        accessor (str): Accessor type for the rule.
        comment (str): Descriptive comment about the rule's purpose.
    """

    guid: UUID = field(default_factory=uuid4)
    name: str
    category: str
    glob: str
    accessor: str
    comment: str

    def to_dict(self) -> dict:
        """Convert to dict.

        Returns:
            dict: Dictionary representation of the rule with string GUID.
        """
        dct = asdict(self)
        dct['guid'] = str(dct['guid'])
        return dct


GUIDRuleMapping = dict[UUID, Rule]


@dataclass(kw_only=True)
class RuleSet:
    """Set of rules.

    Collection of Rule objects indexed by their GUIDs for efficient lookup.

    Attributes:
        by_guid (GUIDRuleMapping): Dictionary mapping rule GUIDs to Rule objects.
    """

    by_guid: GUIDRuleMapping

    @property
    def count(self) -> int:
        """Count of rules in ruleset.

        Returns:
            int: Number of rules in the set.
        """
        return len(self.by_guid)

    @property
    def empty(self) -> bool:
        """Determine if ruleset is empty.

        Returns:
            bool: True if the rule set contains no rules.
        """
        return not bool(self.by_guid)

    @property
    def values(self) -> Iterable[Rule]:
        """Retrieve values.

        Returns:
            Iterable[Rule]: Iterable of all Rule objects in the set.
        """
        return self.by_guid.values()

    @classmethod
    def from_iterable(cls, iterable: Iterable[Rule]):
        """Build from iterable.

        Args:
            iterable (Iterable[Rule]): Iterable of Rule objects to include.

        Returns:
            RuleSet: New RuleSet instance containing the provided rules.
        """
        by_guid = {}
        for rule in iterable:
            if rule.guid in by_guid:
                _LOGGER.warning("duplicate rule: %s", rule.guid)
                continue
            by_guid[rule.guid] = rule
        return cls(by_guid=by_guid)

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build from filepath.

        Args:
            filepath (Path): Path to JSONL file containing rule definitions.

        Returns:
            RuleSet: New RuleSet instance loaded from the file.
        """
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
        """Merge rules from given rule set in this rule set.

        Args:
            rule_set (RuleSet): The RuleSet to merge into this one.

        Returns:
            bool: True if merge was successful, False if duplicates were found.
        """
        guids = set(self.by_guid)
        duplicates = guids.intersection(set(rule_set.by_guid))
        if duplicates:
            _LOGGER.warning("failed to merge, duplicate rules: %s", duplicates)
            return False
        self.by_guid.update(rule_set.by_guid)
        return True
