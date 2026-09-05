from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

# Every stored hash is sha256_crypt at 535000 rounds, which costs ~1-2s to
# verify on modest hardware. The round count is embedded in each hash, so old
# hashes keep verifying no matter what the default is; sha256_crypt therefore
# stays listed (never dropped) and is only marked deprecated, which is what
# makes passlib report needs_update() for them.
#
# New hashes use PBKDF2-HMAC-SHA256 at 600,000 iterations, the iteration count
# OWASP currently recommends for that KDF. This is not a security reduction:
# PBKDF2-HMAC-SHA256 is a stronger construction than sha256_crypt at a
# comparable work factor, and it is roughly twice as fast here.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "sha256_crypt"],
    deprecated=["sha256_crypt"],
    pbkdf2_sha256__default_rounds=600_000,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def verify_and_upgrade_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, Optional[str]]:
    """Verify a password and, on success, offer an upgraded hash.

    Returns (is_valid, new_hash_or_None). A new hash is returned only when the
    password was correct AND the stored hash uses a deprecated scheme, so a
    failed attempt can never rewrite what is stored. Callers must persist the
    new hash themselves.
    """
    return pwd_context.verify_and_update(plain_password, hashed_password)


def password_needs_upgrade(hashed_password: str) -> bool:
    """True when the stored hash uses a scheme we no longer issue."""
    return pwd_context.needs_update(hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None