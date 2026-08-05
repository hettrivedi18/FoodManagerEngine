import asyncio
from fastmcp import Client

async def main():
    async with Client("server.py") as client:
        result = await client.call_tool("get_inventory", {})
        print(result)

asyncio.run(main())