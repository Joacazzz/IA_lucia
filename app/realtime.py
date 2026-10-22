import asyncio

from fastapi import WebSocket


class WSManager:
    def __init__(self) -> None:
        self._conns: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._conns.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._conns.discard(ws)

    async def broadcast(self, msg: dict) -> None:
        if not self._conns:
            return
        conns = list(self._conns)
        results = await asyncio.gather(*(c.send_json(msg) for c in conns), return_exceptions=True)
        for c, r in zip(conns, results):
            if isinstance(r, Exception):
                self.disconnect(c)


manager = WSManager()
