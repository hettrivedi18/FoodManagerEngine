from fastmcp import FastMCP
from database import get_connection

mcp = FastMCP("Food Manager Engine")

@mcp.tool()
def get_inventory():
    """Returns current stock levels for all inventory items, including name, quantity, unit, and expiry date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__=="__main__":
    mcp.run()