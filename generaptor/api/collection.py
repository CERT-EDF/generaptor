"""Collection API
"""
import typing as t
from json import loads
from pathlib import Path
from zipfile import ZipFile
from dataclasses import dataclass
from pyzipper import AESZipFile
from ..helper.crypto import RSAPrivateKey, decrypt_secret, checksum
from ..helper.logging import LOGGER


_DATA_FILENAME = 'data.zip'


@dataclass
class Collection:
    """Collection archive"""

    filepath: Path

    @property
    def metadata(self) -> t.Mapping[str, str]:
        """Collection metadata"""
        if not hasattr(self, '__metadata'):
            with ZipFile(self.filepath) as zipf:
                zipinf = zipf.getinfo('metadata.json')
                data = zipf.read(zipinf)
                (__metadata,) = loads(data.decode())
            setattr(self, '__metadata', __metadata)
        return getattr(self, '__metadata')

    @property
    def checksum(self) -> str:
        """Compute SHA-256 sum of the collection"""
        if not hasattr(self, '__checksum'):
            __checksum = checksum(self.filepath)
            setattr(self, '__checksum', __checksum)
        return getattr(self, '__checksum')

    @property
    def hostname(self) -> t.Optional[str]:
        """Retrieve hostname in metadata"""
        return self.metadata.get('hostname')

    @property
    def device(self) -> t.Optional[str]:
        """Retrieve hostname in metadata"""
        return self.metadata.get('device')

    @property
    def fingerprint(self) -> t.Optional[str]:
        """Retrieve public key fingerprint in metadata"""
        return self.metadata.get('fingerprint_hex')

    def secret(self, private_key: RSAPrivateKey) -> t.Optional[str]:
        """Retrieve collection secret"""
        b64_enc_secret = self.metadata.get('b64_enc_secret')
        if not b64_enc_secret:
            return None
        secret_bytes = decrypt_secret(private_key, b64_enc_secret)
        return secret_bytes.decode()

    def extract_to(self, directory: Path, secret: str) -> bool:
        """Extract collection archive data to directory"""
        # extract and decrypt data.zip archive
        LOGGER.info("extracting and decrypting %s", _DATA_FILENAME)
        try:
            with AESZipFile(str(self.filepath), 'r') as zipf:
                zipf.setpassword(secret.encode('utf-8'))
                zipf.extract(_DATA_FILENAME, path=str(directory))
        except RuntimeError:
            LOGGER.exception("encrypted archive extraction failed!")
            return False
        # extract data.zip content
        LOGGER.info("extracting %s content", _DATA_FILENAME)
        success = True
        data_filepath = directory / _DATA_FILENAME
        try:
            with ZipFile(data_filepath, 'r') as zipf:
                zipf.extractall(path=directory)
        except:
            success = False
            LOGGER.exception("data archive extraction failed!")
        finally:
            data_filepath.unlink()
        return success


CollectionList = t.List[Collection]
