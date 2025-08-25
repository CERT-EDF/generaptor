"""Generaptor Collection"""

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
    """Outcome"""

    SUCCESS = 'success'
    PARTIAL = 'partial'
    FAILURE = 'failure'


def _extract_zip_to(filepath: Path, directory: Path) -> Outcome:
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
    """Collection archive"""

    filepath: Path

    @cached_property
    def metadata(self) -> dict[str, str]:
        """Collection metadata"""
        with ZipFile(self.filepath) as zipf:
            zipinf = zipf.getinfo('metadata.json')
            data = zipf.read(zipinf)
            return loads(data.decode())[0]

    @cached_property
    def checksum(self) -> str:
        """Compute SHA-256 sum of the collection"""
        return checksum(self.filepath)

    @cached_property
    def version(self) -> str | None:
        """Retrieve version in metadata"""
        return self.metadata.get('version')

    @cached_property
    def created(self) -> datetime | None:
        """Retrieve creation timestamp in metadata"""
        dtv = self.metadata.get('created')
        if not dtv:
            return None
        return datetime.fromisoformat(dtv)

    @cached_property
    def opsystem(self) -> OperatingSystem | None:
        """Retrieve operating system in metadata"""
        opsystem = self.metadata.get('opsystem')
        if not opsystem:
            return None
        return OperatingSystem(opsystem)

    @cached_property
    def hostname(self) -> str | None:
        """Retrieve hostname in metadata"""
        return self.metadata.get('hostname')

    @cached_property
    def device(self) -> str | None:
        """Retrieve hostname in metadata"""
        return self.metadata.get('device')

    @cached_property
    def fingerprint(self) -> str | None:
        """Retrieve public key fingerprint in metadata"""
        return self.metadata.get('fingerprint_hex')

    def secret(self, private_key: RSAPrivateKey) -> str | None:
        """Retrieve collection secret"""
        b64_enc_secret = self.metadata.get('b64_enc_secret')
        if not b64_enc_secret:
            return None
        secret_bytes = decrypt_secret(private_key, b64_enc_secret)
        return secret_bytes.decode()

    def extract_to(self, directory: Path, secret: str) -> Outcome:
        """Extract collection archive data to directory"""
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
