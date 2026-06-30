"""Generaptor Profile module.

This module provides data structures for managing profiles in generaptor,
including the Profile class and ProfileSet collection.
"""

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from uuid import UUID, uuid4

from ..helper.json import load_jsonl
from ..helper.logging import get_logger

_LOGGER = get_logger('concept.profileset')


@dataclass(kw_only=True, frozen=True)
class Profile:
    """Profile.

    Represents a collection profile that groups multiple targets together.

    Attributes:
        guid (UUID): Unique identifier for the profile.
        name (str): Human-readable name of the profile.
        targets (set[UUID]): Set of target GUIDs that this profile includes.
    """

    guid: UUID = field(default_factory=uuid4)
    name: str
    targets: set[UUID]

    def to_dict(self) -> dict:
        """Convert to dict.

        Returns:
            dict: Dictionary representation of the profile with string GUID and targets.
        """
        dct = asdict(self)
        dct['guid'] = str(dct['guid'])
        dct['targets'] = list(sorted(map(str, dct['targets'])))
        return dct


NameProfileMapping = dict[str, Profile]
GUIDProfileMapping = dict[UUID, Profile]


@dataclass(kw_only=True)
class ProfileSet:
    """Profile file.

    Collection of Profile objects indexed by both name and GUID for efficient lookup.

    Attributes:
        by_name (NameProfileMapping): Dictionary mapping profile names to Profile objects.
        by_guid (GUIDProfileMapping): Dictionary mapping profile GUIDs to Profile objects.
    """

    by_name: NameProfileMapping
    by_guid: GUIDProfileMapping

    @property
    def count(self):
        """Count of profile in profileset.

        Returns:
            int: Number of profiles in the set.
        """
        return len(self.by_guid)

    @property
    def empty(self) -> bool:
        """Determine if profileset is empty.

        Returns:
            bool: True if the profile set contains no profiles.
        """
        return not bool(self.by_guid)

    @property
    def values(self) -> Iterable[Profile]:
        """Retrieve values.

        Returns:
            Iterable[Profile]: Iterable of all Profile objects in the set.
        """
        return self.by_guid.values()

    @classmethod
    def from_iterable(cls, iterable: Iterable[Profile]):
        """Build from iterable.

        Args:
            iterable (Iterable[Profile]): Iterable of Profile objects to include.

        Returns:
            ProfileSet: New ProfileSet instance containing the provided profiles.
        """
        by_name = {}
        by_guid = {}
        for profile in iterable:
            if profile.name in by_name:
                _LOGGER.warning("duplicate profile: %s", profile.name)
                continue
            by_name[profile.name] = profile
            if profile.guid in by_guid:
                _LOGGER.warning("duplicate profile: %s", profile.guid)
                continue
            by_guid[profile.guid] = profile
        return cls(by_name=by_name, by_guid=by_guid)

    @classmethod
    def from_filepath(cls, filepath: Path):
        """Build from filepath.

        Args:
            filepath (Path): Path to JSONL file containing profile definitions.

        Returns:
            ProfileSet: New ProfileSet instance loaded from the file.
        """
        return cls.from_iterable(
            Profile(
                guid=UUID(row['guid']),
                name=row['name'],
                targets=set(map(UUID, row['targets'])),
            )
            for row in load_jsonl(filepath)
        )

    def merge(self, profile_set: 'ProfileSet') -> bool:
        """Merge given profile set in this profile set.

        Args:
            profile_set (ProfileSet): The ProfileSet to merge into this one.

        Returns:
            bool: True if merge was successful, False if duplicates were found.
        """
        names = set(self.by_name)
        duplicates = names.intersection(set(profile_set.by_name))
        if duplicates:
            _LOGGER.warning(
                "failed to merge profiles (duplicates): %s", duplicates
            )
            return False
        guids = set(self.by_guid)
        duplicates = guids.intersection(set(profile_set.by_guid))
        if duplicates:
            _LOGGER.warning(
                "failed to merge profiles (duplicates): %s", duplicates
            )
            return False
        self.by_name.update(profile_set.by_name)
        self.by_guid.update(profile_set.by_guid)
        return True
