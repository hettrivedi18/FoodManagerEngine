from fastmcp import FastMCP
from database import get_connection
from datetime import date, timedelta

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


@mcp.tool()
def check_waste_risk():
    """Identifies inventory items likely to expire within the next 3 days."""
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()
    threshold_date= today+timedelta(days=3)
    cursor.execute("SELECT * FROM inventory WHERE expiry_date is NOT NULL AND expiry_date<= ?", (str(threshold_date),))
    rows= cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__=="__main__":
    mcp.run()
