import asyncio
from fastmcp import Client

async def main():
    async with Client("server.py") as client:
        inventory = await client.call_tool("get_inventory", {})
        print("INVENTORY:", inventory)

        waste_risk = await client.call_tool("check_waste_risk", {})
        print("WASTE RISK:", waste_risk)

asyncio.run(main())