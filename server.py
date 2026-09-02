from fastmcp import FastMCP
from database import get_connection
from datetime import date, timedelta
from sklearn.linear_model import LinearRegression


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

def get_sales_for_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(" SELECT date, quantity_sold FROM sales_history WHERE item_id = ?", (item_id,))
    rows=cursor.fetchall()
    conn.close()
    return rows

def prepare_training_data(item_id):
    rows = get_sales_for_item(item_id)
    X = []
    y = []
    for row in rows:
        d = date.fromisoformat(row["date"])

        if d.weekday() >= 5:
            is_weekend = 1
        else:
            is_weekend = 0

        X.append([is_weekend])
        y.append(row["quantity_sold"])

    return X, y

def predict_for_item(item_id, target_is_weekend):
    X, y = prepare_training_data(item_id)
    model = LinearRegression()
    model.fit(X, y)
    prediction = model.predict([[target_is_weekend]])

    return round(prediction[0], 2)

@mcp.tool()
def predict_demand(target_date: str):
    """Predicts how much of each inventory item will sell on a given date (YYYY-MM-DD)."""
    d = date.fromisoformat(target_date)
    is_weekend = 1 if d.weekday() >= 5 else 0

    items = get_inventory()  

    results = []
    for item in items:
        predicted_qty = int(round(predict_for_item(item["item_id"], is_weekend)))
        results.append({
            "item_id": item["item_id"],
            "name": item["name"],
            "predicted_quantity": predicted_qty
        })

    return results

@mcp.tool()
def recommend_order(target_date: str):
    """Recommends purchase quantities for each inventory item based on predicted demand, current stock, and waste risk."""
    predicted = predict_demand(target_date)
    current_inventory = get_inventory()
    waste_risk_items = check_waste_risk()

    waste_risk_ids = {item["item_id"] for item in waste_risk_items}
    inventory_lookup = {item["item_id"]: item["quantity"] for item in current_inventory}

    results = []
    for pred_item in predicted:
        item_id = pred_item["item_id"]
        predicted_qty = pred_item["predicted_quantity"]
        current_qty = inventory_lookup.get(item_id, 0)
        shortfall = predicted_qty - current_qty

        results.append({
            "item_id": item_id,
            "name": pred_item["name"],
            "current_quantity": current_qty,
            "predicted_quantity": predicted_qty,
            "recommended_order_qty": shortfall if shortfall > 0 else 0,
            "is_waste_risk": item_id in waste_risk_ids
        })

    return results


if __name__=="__main__":
    mcp.run()
    
