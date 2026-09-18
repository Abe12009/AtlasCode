"""In-process WebSocket connection registry for live duels.

Maps duel_id -> {user_id: WebSocket}. Deliberately in-memory, not backed by
Redis or any other cross-process pub/sub -- render.yaml currently runs one
`uvicorn` process with no worker pool, so every connection for a given duel
is guaranteed to be held by this same process. This breaks silently if the
app ever moves to multiple instances/workers (two players could land on
different processes and never see each other's updates); that tradeoff was
called out explicitly in the Step 4 architecture proposal and accepted for
v1 rather than adding Redis infra this app doesn't otherwise need.

What actually goes out over the wire is limited on purpose: opponent
progress is {passed_count, total_count} only, never code, never even which
specific assertions passed -- see app.services.duels.submit_solution, which
is the only thing that calls broadcast_to_opponent with real content. This
module has no code path that could serialize a student's submitted code
into a message, by construction (it only ever forwards dicts its caller
builds).
"""

from typing import Any, Optional

from fastapi import WebSocket


class DuelConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, duel_id: int, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(duel_id, {})[user_id] = websocket

    def disconnect(self, duel_id: int, user_id: int) -> None:
        duel_conns = self._connections.get(duel_id)
        if not duel_conns:
            return
        duel_conns.pop(user_id, None)
        if not duel_conns:
            self._connections.pop(duel_id, None)

    def is_connected(self, duel_id: int, user_id: int) -> bool:
        return user_id in self._connections.get(duel_id, {})

    async def send_to_user(self, duel_id: int, user_id: int, message: dict[str, Any]) -> bool:
        """Best-effort: a send failure just means that socket is already
        dead and hasn't been cleaned up by its own receive-loop yet (see
        app.api.duels' WebSocket handler) -- not this function's job to
        retry or raise."""
        ws = self._connections.get(duel_id, {}).get(user_id)
        if ws is None:
            return False
        try:
            await ws.send_json(message)
            return True
        except Exception:
            return False

    async def broadcast_to_opponent(self, duel_id: int, sender_user_id: int, message: dict[str, Any]) -> None:
        for user_id in list(self._connections.get(duel_id, {}).keys()):
            if user_id != sender_user_id:
                await self.send_to_user(duel_id, user_id, message)

    async def broadcast_to_all(self, duel_id: int, message: dict[str, Any]) -> None:
        for user_id in list(self._connections.get(duel_id, {}).keys()):
            await self.send_to_user(duel_id, user_id, message)


#: One instance for the whole process -- imported by both the WebSocket
#: endpoint (registers/removes connections) and the submit endpoint
#: (pushes progress/end-of-duel events), so they share the same registry.
connection_manager = DuelConnectionManager()
