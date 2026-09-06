"""Server-side verification of Firebase Authentication ID tokens.

Why this exists
---------------
The browser can obtain a Firebase ID token for a user who signed in with
Google, GitHub or an email/password credential. That token is *not* a session:
anything the client sends can be forged, so the backend never trusts it on
sight. This module verifies the token the way Firebase documents it:

  * the signature is checked against Google's published public keys for the
    ``securetoken@system.gserviceaccount.com`` service account (RS256),
  * ``aud`` must equal our Firebase project id,
  * ``iss`` must be ``https://securetoken.google.com/<project id>``,
  * ``exp``/``iat`` must be sane and ``sub`` must be a non-empty user id.

Only after all of that does the caller learn who the user is.

No Firebase *admin* credential is involved, so there is no service-account
private key to store, leak, or rotate — the keys used here are Google's public
signing certificates. Configuration is therefore a single public value,
``FIREBASE_PROJECT_ID``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional

import httpx
from jose import jwt
from jose.exceptions import JWTError

from app.core.config import get_settings

#: Google's JWKS for Firebase ID tokens, in JWK form (python-jose consumes it
#: directly, unlike the x509 endpoint which would need certificate parsing).
GOOGLE_JWKS_URL = "https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com"

#: Google rotates these keys roughly daily and serves them with a long
#: max-age. Re-fetching once an hour is well inside that window while keeping
#: the request cost negligible.
_JWKS_TTL_SECONDS = 3600

#: A token whose `kid` is unknown may mean the keys just rotated. Allow one
#: forced refresh at most this often so a bad token cannot be used to hammer
#: Google's endpoint.
_JWKS_MIN_REFRESH_INTERVAL_SECONDS = 60


class FirebaseAuthError(Exception):
    """Raised when a Firebase ID token cannot be trusted."""


class FirebaseNotConfigured(FirebaseAuthError):
    """Raised when the deployment has no Firebase project configured."""


@dataclass(frozen=True)
class FirebaseIdentity:
    """The verified claims we care about, and nothing else."""

    uid: str
    email: Optional[str]
    email_verified: bool
    name: Optional[str]
    picture: Optional[str]
    #: "password", "google.com", "github.com", …
    sign_in_provider: str


class _JwksCache:
    """Process-local cache of Google's signing keys."""

    def __init__(self) -> None:
        self._keys: dict[str, dict[str, Any]] = {}
        self._fetched_at: float = 0.0
        self._last_forced_refresh: float = 0.0

    def _is_stale(self) -> bool:
        return not self._keys or (time.monotonic() - self._fetched_at) > _JWKS_TTL_SECONDS

    async def _fetch(self) -> None:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(GOOGLE_JWKS_URL)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise FirebaseAuthError("Could not retrieve Google signing keys") from exc

        keys = {key["kid"]: key for key in payload.get("keys", []) if "kid" in key}
        if not keys:
            raise FirebaseAuthError("Google signing key set was empty")
        self._keys = keys
        self._fetched_at = time.monotonic()

    async def get(self, kid: str) -> dict[str, Any]:
        if self._is_stale():
            await self._fetch()
        key = self._keys.get(kid)
        if key is not None:
            return key

        # Unknown key id: keys may have rotated between our last fetch and this
        # token being minted. Refresh once, rate-limited.
        now = time.monotonic()
        if (now - self._last_forced_refresh) > _JWKS_MIN_REFRESH_INTERVAL_SECONDS:
            self._last_forced_refresh = now
            await self._fetch()
            key = self._keys.get(kid)
            if key is not None:
                return key
        raise FirebaseAuthError("Token was signed with an unrecognised key")

    def clear(self) -> None:
        """Test seam: drop cached keys."""
        self._keys = {}
        self._fetched_at = 0.0
        self._last_forced_refresh = 0.0


_jwks_cache = _JwksCache()


def is_firebase_configured() -> bool:
    """True when this deployment can verify Firebase tokens at all."""
    return bool(get_settings().firebase_project_id)


async def verify_firebase_id_token(id_token: str) -> FirebaseIdentity:
    """Verify a Firebase ID token and return the identity it asserts.

    Raises ``FirebaseNotConfigured`` when no project is configured and
    ``FirebaseAuthError`` for every kind of invalid, expired or foreign token.
    The message is deliberately generic so it can be shown to a client without
    revealing which check failed.
    """
    settings = get_settings()
    project_id = settings.firebase_project_id
    if not project_id:
        raise FirebaseNotConfigured(
            "Firebase authentication is not configured on this server"
        )

    if not id_token or not isinstance(id_token, str):
        raise FirebaseAuthError("Missing identity token")

    try:
        header = jwt.get_unverified_header(id_token)
    except JWTError as exc:
        raise FirebaseAuthError("Malformed identity token") from exc

    if header.get("alg") != "RS256":
        # Firebase always signs with RS256; anything else is an attempt to
        # slip past verification (e.g. alg=none or a symmetric key).
        raise FirebaseAuthError("Unexpected token signing algorithm")

    kid = header.get("kid")
    if not kid:
        raise FirebaseAuthError("Identity token has no key id")

    key = await _jwks_cache.get(kid)

    try:
        claims = jwt.decode(
            id_token,
            key,
            algorithms=["RS256"],
            audience=project_id,
            issuer=f"https://securetoken.google.com/{project_id}",
            options={"require_exp": True, "require_iat": True, "verify_at_hash": False},
        )
    except JWTError as exc:
        raise FirebaseAuthError("Identity token is invalid or has expired") from exc

    uid = claims.get("sub") or claims.get("user_id")
    if not uid or not isinstance(uid, str):
        raise FirebaseAuthError("Identity token has no subject")

    firebase_claims = claims.get("firebase") or {}
    provider = firebase_claims.get("sign_in_provider") or "unknown"

    email = claims.get("email")
    return FirebaseIdentity(
        uid=uid,
        email=email.lower().strip() if isinstance(email, str) else None,
        email_verified=bool(claims.get("email_verified")),
        name=claims.get("name") or None,
        picture=claims.get("picture") or None,
        sign_in_provider=provider,
    )
