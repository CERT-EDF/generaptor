"""Generaptor Collection module.

This module provides functionality for handling Velociraptor collection archives,
including extraction, metadata access, and secret retrieval.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import cached_property
from json import loads
from pathlib import Path
from zipfile import ZipFile

from pyzipper import AESZipFile

from ..helper.crypto import RSAPrivateKey, checksum, decrypt_secret
from ..helper.logging import get_logger
from .distribution import OperatingSystem

_LOGGER = get_logger('concept.collection')
_DATA_FILENAME = 'data.zip'


class Outcome(Enum):
    """Outcome.

    Enumeration representing the result of a collection operation.

    Attributes:
        SUCCESS: Operation completed successfully.
        PARTIAL: Operation completed with some errors.
        FAILURE: Operation failed completely.
    """

    SUCCESS = 'success'
    PARTIAL = 'partial'
    FAILURE = 'failure'


def _extract_zip_to(filepath: Path, directory: Path) -> Outcome:
    """Extract ZIP file contents to directory.

    Args:
        filepath (Path): Path to the ZIP file to extract.
        directory (Path): Destination directory for extracted files.

    Returns:
        Outcome: SUCCESS if all files extracted, PARTIAL if some failed, FAILURE if major error.
    """
    outcome = Outcome.SUCCESS
    with ZipFile(filepath, 'r') as zipf:
        for member in zipf.infolist():
            if member.is_dir():
                continue
            try:
                zipf.extract(member, path=directory)
            except OSError as exc:
                outcome = Outcome.PARTIAL
                _LOGGER.warning(
                    "failed to extract member: %s (%s)",
                    member.filename,
                    exc,
                )
    return outcome


@dataclass(frozen=True)
class Collection:
    """Collection archive.

    Represents a Velociraptor collection archive with metadata and data.

    Attributes:
        filepath (Path): Path to the collection ZIP archive file.
    """

    filepath: Path

    @cached_property
    def metadata(self) -> dict[str, str]:
        """Collection metadata.

        Returns:
            dict[str, str]: Metadata dictionary extracted from the collection archive.
        """
        with ZipFile(self.filepath) as zipf:
            zipinf = zipf.getinfo('metadata.json')
            data = zipf.read(zipinf)
            return loads(data.decode())[0]

    @cached_property
    def checksum(self) -> str:
        """Compute SHA-256 sum of the collection.

        Returns:
            str: SHA-256 checksum of the collection file.
        """
        return checksum(self.filepath)

    @cached_property
    def version(self) -> str | None:
        """Retrieve version in metadata.

        Returns:
            str | None: Version string from metadata, or None if not present.
        """
        return self.metadata.get('version')

    @cached_property
    def created(self) -> datetime | None:
        """Retrieve creation timestamp in metadata.

        Returns:
            datetime | None: Creation timestamp from metadata, or None if not present.
        """
        dtv = self.metadata.get('created')
        if not dtv:
            return None
        return datetime.fromisoformat(dtv)

    @cached_property
    def opsystem(self) -> OperatingSystem | None:
        """Retrieve operating system in metadata.

        Returns:
            OperatingSystem | None: Operating system from metadata, or None if not present.
        """
        opsystem = self.metadata.get('opsystem')
        if not opsystem:
            return None
        return OperatingSystem(opsystem)

    @cached_property
    def hostname(self) -> str | None:
        """Retrieve hostname in metadata.

        Returns:
            str | None: Hostname from metadata, or None if not present.
        """
        return self.metadata.get('hostname')

    @cached_property
    def device(self) -> str | None:
        """Retrieve device name in metadata.

        Returns:
            str | None: Device name from metadata, or None if not present.
        """
        return self.metadata.get('device')

    @cached_property
    def fingerprint(self) -> str | None:
        """Retrieve public key fingerprint in metadata.

        Returns:
            str | None: Fingerprint from metadata, or None if not present.
        """
        return self.metadata.get('fingerprint_hex')

    def secret(self, private_key: RSAPrivateKey) -> str | None:
        """Retrieve collection secret.

        Args:
            private_key (RSAPrivateKey): Private key for decrypting the secret.

        Returns:
            str | None: Decrypted secret string, or None if not present/valid.
        """
        b64_enc_secret = self.metadata.get('b64_enc_secret')
        if not b64_enc_secret:
            return None
        secret_bytes = decrypt_secret(private_key, b64_enc_secret)
        return secret_bytes.decode()

    def extract_to(self, directory: Path, secret: str) -> Outcome:
        """Extract collection archive data to directory.

        Extracts and decrypts the encrypted data.zip archive from the collection.

        Args:
            directory (Path): Destination directory for extracted data.
            secret (str): Secret/password for decrypting the archive.

        Returns:
            Outcome: Result of the extraction operation.
        """
        # extract and decrypt data.zip archive
        outcome = Outcome.FAILURE
        _LOGGER.info("extracting and decrypting %s", _DATA_FILENAME)
        try:
            with AESZipFile(str(self.filepath), 'r') as zipf:
                zipf.setpassword(secret.encode('utf-8'))
                zipf.extract(_DATA_FILENAME, path=str(directory))
        except RuntimeError:
            _LOGGER.exception("encrypted archive extraction failed!")
            return outcome
        # extract data.zip content
        _LOGGER.info("extracting %s content", _DATA_FILENAME)
        data_filepath = directory / _DATA_FILENAME
        try:
            outcome = _extract_zip_to(data_filepath, directory)
        except:
            _LOGGER.exception("data archive extraction failed!")
        finally:
            data_filepath.unlink()
        return outcome


CollectionList = list[Collection]
