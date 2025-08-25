"""Cryptography helper"""

from base64 import b64decode
from datetime import datetime, timedelta, timezone
from getpass import getpass
from os import getenv
from pathlib import Path
from secrets import token_urlsafe

from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKey,
    generate_private_key,
)
from cryptography.hazmat.primitives.hashes import SHA256, SHA512, Hash
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption,
    Encoding,
    PrivateFormat,
    load_pem_private_key,
)
from cryptography.x509 import (
    Certificate,
    CertificateBuilder,
    DNSName,
    Name,
    NameAttribute,
    SubjectAlternativeName,
    load_pem_x509_certificate,
    random_serial_number,
)
from cryptography.x509.oid import NameOID

from .logging import get_logger

_LOGGER = get_logger('helper.crypto')
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


def generate_private_key_and_certificate(
    validity: timedelta = timedelta(days=30),
    common_name: str = 'generaptor',
    key_size: int = RSA_KEY_SIZE,
    public_exponent: int = RSA_PUBLIC_EXPONENT,
) -> tuple[RSAPrivateKey, Certificate]:
    """Generate (private_key, certificate)"""
    _LOGGER.info("generating private key... please wait...")
    private_key = generate_private_key(
        public_exponent=public_exponent,
        key_size=key_size,
    )
    subject_name = issuer_name = Name(
        [
            NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
    )
    utc_now = datetime.now(timezone.utc)
    _LOGGER.info("generating certificate...")
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
            utc_now + validity,
        )
        .add_extension(
            SubjectAlternativeName([DNSName(common_name)]),
            critical=False,
        )
        .sign(private_key, SHA256())
    )
    return private_key, certificate


def private_key_to_pem_bytes(
    private_key: RSAPrivateKey, private_key_secret: bytes
) -> bytes:
    """RSA private key to PEM bytes"""
    return private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=BestAvailableEncryption(private_key_secret),
    )


def private_key_from_pem_bytes(
    pem_bytes: bytes, private_key_secret: bytes
) -> RSAPrivateKey:
    """RSA private key from PEM bytes"""
    return load_pem_private_key(pem_bytes, private_key_secret)


def certificate_to_pem_bytes(certificate: Certificate) -> bytes:
    """Certificate to PEM bytes"""
    return certificate.public_bytes(Encoding.PEM)


def certificate_from_pem_bytes(pem_bytes: bytes) -> Certificate:
    """Certificate from PEM bytes"""
    return load_pem_x509_certificate(pem_bytes)


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
        _LOGGER.warning("private key secret is %s", private_key_secret)
        _LOGGER.warning("store this secret in a vault please!")
    return private_key_secret


def _generate_self_signed_certificate(
    output_directory: Path,
    ask_password: bool = False,
    private_key_secret: str | None = None,
) -> Certificate:
    private_key, certificate = generate_private_key_and_certificate()
    # ensure output directory exists
    output_directory.mkdir(parents=True, exist_ok=True)
    # retrieve private key password
    private_key_secret = private_key_secret or _provide_private_key_secret(
        ask_password=ask_password
    )
    private_key_secret = private_key_secret.encode('utf-8')
    fingerprint_hex = fingerprint(certificate)
    # store encrypted private key in a file
    (output_directory / f'{fingerprint_hex}.key.pem').write_bytes(
        private_key_to_pem_bytes(private_key, private_key_secret)
    )
    # store certificate in a file
    (output_directory / f'{fingerprint_hex}.crt.pem').write_bytes(
        certificate_to_pem_bytes(certificate)
    )
    return certificate


def provide_x509_certificate(
    output_directory: Path,
    cert_filepath: Path | None = None,
    ask_password: bool = False,
    private_key_secret: str | None = None,
) -> Certificate:
    """Provide x509 certificate"""
    if cert_filepath and cert_filepath.is_file():
        certificate = certificate_from_pem_bytes(cert_filepath.read_bytes())
        _LOGGER.info(
            "using certificate %s fingerprint %s",
            cert_filepath,
            fingerprint(certificate),
        )
        return certificate
    return _generate_self_signed_certificate(
        output_directory, ask_password, private_key_secret
    )


def load_private_key(
    private_key_path: Path, private_key_secret: str | None = None
) -> RSAPrivateKey | None:
    """Load PEM encoded encrypted private key from file"""
    try:
        private_key_secret = private_key_secret or _provide_private_key_secret(
            ask_password=True, raise_if_generate=True
        )
    except (ValueError, KeyboardInterrupt):
        private_key_secret = None
    if not private_key_secret:
        _LOGGER.warning("failed to provide private key secret")
        return None
    return private_key_from_pem_bytes(
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
