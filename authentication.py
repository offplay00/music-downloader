import asyncio
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music_microservices.settings")

django.setup()

from sesame.utils import get_user
from websockets.asyncio.server import serve
from websockets.frames import CloseCode

async def handler(websocket):
    sesame = await websocket.recv()
    user = await asyncio.to_thread(get_user, sesame)
    if user is None:
        await websocket.close(CloseCode.INTERNAL_ERROR, "authentication failed")
        return websocket.send("authentication failed")

    await websocket.send(f"Hello {user}!")


async def main():
    async with serve(handler, "localhost", 8888) as server:
        await server.serve_forever()


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())