"""Short-lived WebSocket auth tickets.

A browser can't attach a custom Authorization header to a WebSocket upgrade
request, so the existing OAuth2PasswordBearer flow (app.core.dependencies.
get_current_user) doesn't carry over to `/ws/duels/{id}`. Rather than put
the student's real, reusable access token in a URL (query params end up in
proxy/server logs), the client mints a ticket via an ordinary authenticated
REST call right before opening the socket, and passes *that* instead: a
single-use, ~20-second-lived, duel-scoped random token that's worthless
after one successful connection (or after it expires unused).

In-process, module-level storage -- consistent with the connection manager
in duel_realtime.py and the documented "single Render instance" v1
simplification from the architecture proposal. A ticket minted on one
process wouldn't be visible to another, which matters only if this ever
runs on more than one instance (same caveat as the connection manager).
"""

import secrets
import time
from dataclasses import dataclass
from typing import Optional

#: Long enough for "REST call returns, browser opens the socket" to always
#: succeed even under real network latency; short enough that a leaked
#: ticket (e.g. in a browser history entry, if a query param) is useless
#: within seconds.
TICKET_TTL_SECONDS = 20.0


@dataclass
class _Ticket:
    user_id: int
    duel_id: int
    expires_at: float  # time.monotonic()-based, not wall-clock


#: Not bounded/swept -- at expected duel-arena scale (a handful of
#: concurrent duels) this is a non-issue; a ticket that's never consumed
#: just sits here until process restart. Worth revisiting only if this ever
#: needs to run at a scale where that matters.
_tickets: dict[str, _Ticket] = {}


def mint_ticket(user_id: int, duel_id: int) -> str:
    token = secrets.token_urlsafe(32)
    _tickets[token] = _Ticket(user_id=user_id, duel_id=duel_id, expires_at=time.monotonic() + TICKET_TTL_SECONDS)
    return token


def consume_ticket(token: str, duel_id: int) -> Optional[int]:
    """Validates and single-use-consumes a ticket scoped to `duel_id`.
    Returns the minting user's id on success; None if the ticket doesn't
    exist, was already used, was minted for a different duel, or has
    expired. The ticket is removed from the store on a successful
    consumption (single-use) but is deliberately left in place otherwise --
    an invalid attempt shouldn't destroy a ticket a legitimate retry (e.g.
    the same request racing a slow network) might still need."""
    ticket = _tickets.get(token)
    if ticket is None:
        return None
    if ticket.duel_id != duel_id or time.monotonic() > ticket.expires_at:
        return None
    del _tickets[token]
    return ticket.user_id
