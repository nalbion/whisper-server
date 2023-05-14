import asyncio
from .app import main

async def try_main():
    try:
        await main()
    except KeyboardInterrupt:
        pass

try:
    asyncio.run(try_main())
except KeyboardInterrupt:
    pass
