from flask import Flask, jsonify, request
from fastmcp import Client
import asyncio
import json

app = Flask(__name__)

MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"

def call_mcp_tool(tool_name, arguments=None):
    if arguments is None:
        arguments = {}

    async def call():
        async with Client(MCP_SERVER_URL) as client:
            result = await client.call_tool(tool_name, arguments)
            return result

    result = asyncio.run(call())
    return json.loads(result.content[0].text)

@app.route("/api/inventory")
def api_inventory():
    return jsonify(call_mcp_tool("get_inventory"))

@app.route("/api/waste-risk")
def api_waste_risk():
    return jsonify(call_mcp_tool("check_waste_risk"))

@app.route("/api/predict")
def api_predict():
    target_date = request.args.get("date")
    return jsonify(call_mcp_tool("predict_demand", {"target_date": target_date}))

@app.route("/api/recommend")
def api_recommend():
    target_date = request.args.get("date")
    return jsonify(call_mcp_tool("recommend_order", {"target_date": target_date}))

if __name__ == "__main__":
    app.run(debug=True, port=5000)