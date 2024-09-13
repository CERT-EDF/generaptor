"""Cryptography helper
"""

from os import getenv
from typing import Optional
from base64 import b64decode
from pathlib import Path
from getpass import getpass
from secrets import token_urlsafe
from datetime import datetime, timedelta, timezone
from cryptography.x509 import (
    load_pem_x509_certificate,
    random_serial_number,
    SubjectAlternativeName,
    CertificateBuilder,
    NameAttribute,
    Certificate,
    DNSName,
    Name,
)
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.hashes import Hash, SHA256, SHA512
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    BestAvailableEncryption,
    PrivateFormat,
    Encoding,
)
from cryptography.hazmat.primitives.asymmetric.rsa import (
    generate_private_key,
    RSAPrivateKey,
)
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from .logging import LOGGER


VALIDITY = timedelta(days=30)
CHUNK_SIZE = 8192
RSA_KEY_SIZE = 4096
RSA_PUBLIC_EXPONENT = 65537


def checksum(filepath: Path) -> str:
    """Compute the checksum"""
    digest = Hash(SHA256())
    with filepath.open('rb') as fstream:
        while chunk := fstream.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.finalize().hex()


def fingerprint(certificate: Certificate):
    """Certificate SHA256 fingerprint"""
    return certificate.fingerprint(SHA256()).hex()


def pem_string(certificate: Certificate):
    """Certificate as a PEM string"""
    crt_pem_bytes = certificate.public_bytes(Encoding.PEM)
    crt_pem_string = crt_pem_bytes.decode()
    crt_pem_string = crt_pem_string.replace('\n', '\\n')
    return crt_pem_string


def _provide_private_key_secret(
    ask_password: bool = False, raise_if_generate: bool = False
) -> str:
    # attempt to load the secret from the environment
    private_key_secret = getenv('GENERAPTOR_PK_SECRET')
    # interactively ask the user for the secret if necessary
    if not private_key_secret and ask_password:
        private_key_secret = getpass("private key secret: ")
    # generate and display the secret if necessary
    if not private_key_secret:
        if raise_if_generate:
            raise ValueError("failed to provide private key secret")
        private_key_secret = token_urlsafe(16)
        LOGGER.warning("private key secret is %s", private_key_secret)
        LOGGER.warning("store this secret in a vault please!")
    return private_key_secret


def _generate_self_signed_certificate(
    output_directory: Path,
    ask_password: bool = False,
    private_key_secret: Optional[str] = None,
) -> Certificate:
    LOGGER.info("generating private key... please wait...")
    private_key = generate_private_key(
        public_exponent=RSA_PUBLIC_EXPONENT,
        key_size=RSA_KEY_SIZE,
    )
    subject_name = issuer_name = Name(
        [
            NameAttribute(NameOID.COMMON_NAME, "generaptor"),
        ]
    )
    utc_now = datetime.now(timezone.utc)
    LOGGER.info("generating certificate...")
    certificate = (
        CertificateBuilder()
        .subject_name(
            subject_name,
        )
        .issuer_name(
            issuer_name,
        )
        .public_key(
            private_key.public_key(),
        )
        .serial_number(
            random_serial_number(),
        )
        .not_valid_before(
            utc_now,
        )
        .not_valid_after(
            utc_now + VALIDITY,
        )
        .add_extension(
            SubjectAlternativeName([DNSName("generaptor")]),
            critical=False,
        )
        .sign(private_key, SHA256())
    )
    # ensure output directory exists
    output_directory.mkdir(parents=True, exist_ok=True)
    # retrieve private key password
    private_key_secret = private_key_secret or _provide_private_key_secret(
        ask_password=ask_password
    )
    # store encrypted private key in a file
    fingerprint_hex = fingerprint(certificate)
    (output_directory / f'{fingerprint_hex}.key.pem').write_bytes(
        private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=BestAvailableEncryption(
                private_key_secret.encode()
            ),
        ),
    )
    # store certificate in a file
    crt_pem_bytes = certificate.public_bytes(Encoding.PEM)
    (output_directory / f'{fingerprint_hex}.crt.pem').write_bytes(
        crt_pem_bytes
    )
    return certificate


def load_certificate(cert_filepath: Path):
    """Load certificate from filepath"""
    crt_pem_bytes = cert_filepath.read_bytes()
    return load_pem_x509_certificate(crt_pem_bytes)


def provide_x509_certificate(
    output_directory: Path,
    cert_filepath: Optional[Path] = None,
    ask_password: bool = False,
    private_key_secret: Optional[str] = None,
) -> str:
    """Provide x509 certificate"""
    if cert_filepath and cert_filepath.is_file():
        certificate = load_certificate(cert_filepath)
        LOGGER.info(
            "using certificate %s fingerprint %s",
            cert_filepath,
            fingerprint(certificate),
        )
    else:
        certificate = _generate_self_signed_certificate(
            output_directory, ask_password, private_key_secret
        )
    return certificate


def load_private_key(
    private_key_path: Path, private_key_secret: Optional[str] = None
) -> Optional[RSAPrivateKey]:
    """Load PEM encoded encrypted private key from file"""
    try:
        private_key_secret = private_key_secret or _provide_private_key_secret(
            ask_password=True, raise_if_generate=True
        )
    except (ValueError, KeyboardInterrupt):
        private_key_secret = None
    if not private_key_secret:
        LOGGER.warning("failed to provide private key secret")
        return None
    return load_pem_private_key(
        private_key_path.read_bytes(), private_key_secret.encode()
    )


def decrypt_secret(private_key: RSAPrivateKey, b64_enc_secret: str) -> bytes:
    """Decrypt a base64-encoded secret using given private key"""
    enc_secret = b64decode(b64_enc_secret)
    secret = private_key.decrypt(
        enc_secret,
        OAEP(mgf=MGF1(algorithm=SHA512()), algorithm=SHA512(), label=None),
    )
    return secret
