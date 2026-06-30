"""Generaptor Target Set module.

This module provides data structures for managing targets in generaptor,
including the Target class and TargetSet collection.
"""

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from uuid import UUID, uuid4

from ..helper.json import load_jsonl
from ..helper.logging import get_logger
from ..helper.prompt import Option, multiselect
from .rule_set import RuleSet

_LOGGER = get_logger('concept.targetset')


@dataclass(kw_only=True, frozen=True)
class Target:
    """Target.

    Represents a collection target that groups multiple rules together.

    Attributes:
        guid (UUID): Unique identifier for the target.
        name (str): Human-readable name of the target.
        rules (set[UUID]): Set of rule GUIDs that this target includes.
    """

    guid: UUID = field(default_factory=uuid4)
    name: str
    rules: set[UUID]

    def to_dict(self) -> dict:
        """Convert to dict.

        Returns:
            dict: Dictionary representation of the target with string GUID and rules.
        """
        dct = asdict(self)
        dct['guid'] = str(dct['guid'])
        dct['rules'] = list(sorted(map(str, dct['rules'])))
        return dct


NameTargetMapping = dict[str, Target]
GUIDTargetMapping = dict[UUID, Target]


@dataclass(kw_only=True)
class TargetSet:
    """Set of targets.

    Collection of Target objects indexed by both name and GUID for efficient lookup.

    Attributes:
        by_name (NameTargetMapping): Dictionary mapping target names to Target objects.
        by_guid (GUIDTargetMapping): Dictionary mapping target GUIDs to Target objects.
    """

    by_name: NameTargetMapping
    by_guid: GUIDTargetMapping

    @property
    def count(self):
        """Count of target in targetset.

        Returns:
            int: Number of targets in the set.
        """
        return len(self.by_guid)

    @property
    def empty(self) -> bool:
        """Determine if targetset is empty.

        Returns:
            bool: True if the target set contains no targets.
        """
        return not bool(self.by_guid)

    @property
    def values(self) -> Iterable[Target]:
        """Retrieve values.

        Returns:
            Iterable[Target]: Iterable of all Target objects in the set.
        """
        return self.by_guid.values()

    @classmethod
    def from_iterable(cls, iterable: Iterable[Target]):
        """Build from iterable.

        Args:
            iterable (Iterable[Target]): Iterable of Target objects to include.

        Returns:
            TargetSet: New TargetSet instance containing the provided targets.
        """
        by_name = {}
        by_guid = {}
        for target in iterable:
            if target.name in by_name:
                _LOGGER.warning("duplicate target: %s", target.name)
                continue
            by_name[target.name] = target
            if target.guid in by_guid:
                _LOGGER.warning("duplicate target: %s", target.guid)
                continue
            by_guid[target.guid] = target
        return cls(by_name=by_name, by_guid=by_guid)

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build from filepath.

        Args:
            filepath (Path): Path to JSONL file containing target definitions.

        Returns:
            TargetSet: New TargetSet instance loaded from the file.
        """
        return cls.from_iterable(
            Target(
                guid=UUID(row['guid']),
                name=row['name'],
                rules=set(map(UUID, row['rules'])),
            )
            for row in load_jsonl(filepath)
        )

    def merge(self, target_set: 'TargetSet') -> bool:
        """Merge given target set in this target set.

        Args:
            target_set (TargetSet): The TargetSet to merge into this one.

        Returns:
            bool: True if merge was successful, False if duplicates were found.
        """
        names = set(self.by_name)
        duplicates = names.intersection(set(target_set.by_name))
        if duplicates:
            _LOGGER.warning(
                "failed to merge targets (duplicates): %s", duplicates
            )
            return False
        guids = set(self.by_guid)
        duplicates = guids.intersection(set(target_set.by_guid))
        if duplicates:
            _LOGGER.warning(
                "failed to merge targets (duplicates): %s", duplicates
            )
            return False
        self.by_name.update(target_set.by_name)
        self.by_guid.update(target_set.by_guid)
        return True

    def select(self, rule_set: RuleSet, targets: list[str | UUID]) -> RuleSet:
        """Build a rule set from an existing ruleset and selected targets.

        If no targets are provided, an interactive selection is prompted.

        Args:
            rule_set (RuleSet): The complete rule set to filter from.
            targets (list[str | UUID]): List of target names or GUIDs to include.
                If empty, interactive selection will be used.

        Returns:
            RuleSet: New RuleSet containing only rules from the selected targets.
        """
        if not targets:
            targets = multiselect(
                "Pick one or more collection targets",
                [
                    Option(label=target.name, value=target.name)
                    for target in self.by_name.values()
                ],
            )
        by_guid = {}
        for key in targets:
            by_key = self.by_guid if isinstance(key, UUID) else self.by_name
            target = by_key.get(key)
            if not target:
                _LOGGER.warning("skipped unknown target: %s", key)
                continue
            for guid in target.rules:
                if guid not in rule_set.by_guid:
                    _LOGGER.warning("skipped missing rule: %s", guid)
                    continue
                by_guid[guid] = rule_set.by_guid[guid]
            _LOGGER.info(
                "select %s (%d rules)", target.name, len(target.rules)
            )
        return RuleSet(by_guid=by_guid)
