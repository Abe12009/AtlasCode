"""Transactional email via the Resend REST API.

Calls Resend's HTTP API directly with `httpx`, the same way
`app.services.firebase_auth` talks to Google's JWKS endpoint, rather than
adding the `resend` PyPI package -- one fewer dependency for one endpoint call.
"""

from __future__ import annotations

from html import escape

import httpx

from app.core.config import get_settings

RESEND_API_URL = "https://api.resend.com/emails"


class EmailSendError(Exception):
    """Raised when Resend rejects or cannot be reached for an email send."""


def is_email_configured() -> bool:
    """True when this deployment can send transactional email at all."""
    return bool(get_settings().resend_api_key)


async def send_password_reset_email(to_email: str, reset_url: str) -> None:
    """Send the "reset your password" email. Raises EmailSendError on failure.

    Callers must not let a raised EmailSendError change what they tell the
    client -- see app.api.auth.forgot_password, which always answers the
    same way regardless of whether this send actually succeeded.
    """
    settings = get_settings()
    safe_url = escape(reset_url)
    html = f"""
        <p>Someone asked to reset the password for your AtlasCode account.</p>
        <p><a href="{safe_url}">Reset your password</a></p>
        <p>This link expires in {settings.password_reset_token_expire_minutes}
        minutes. If you didn't request this, you can safely ignore this email.</p>
    """.strip()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                RESEND_API_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={
                    "from": settings.email_from_address,
                    "to": [to_email],
                    "subject": "Reset your AtlasCode password",
                    "html": html,
                },
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise EmailSendError("Could not send password reset email") from exc
