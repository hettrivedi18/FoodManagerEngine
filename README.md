# Food Manager Engine

An AI-powered restaurant operations MCP (Model Context Protocol) server that exposes ML-driven inventory management tools — demand forecasting, waste-risk detection, and purchase recommendations — consumable by Claude or any MCP-compatible client.

This is the V1 foundation of a longer-term project: **MISE — Restaurant Intelligence Engine**, a broader ML-powered platform planned to eventually incorporate weather, holidays, events, and staffing data alongside historical sales.

## What it does

Food Manager Engine exposes four tools over the Model Context Protocol:

| Tool | Description |
|---|---|
| `get_inventory()` | Returns current stock levels for all inventory items (name, quantity, unit, expiry date). |
| `check_waste_risk()` | Identifies inventory items likely to expire within the next 3 days. |
| `predict_demand(date)` | Predicts expected demand per item for a given date, using a linear regression model trained per item on historical sales data. |
| `recommend_order(date)` | Combines predicted demand, current stock, and waste risk to recommend purchase quantities per item. |

Any MCP client (Claude Desktop, a custom agent, etc.) can connect to this server, discover these tools automatically, and call them based on natural-language requests — e.g. "what should I order this week?" → Claude calls `recommend_order`.

## Tech stack

- **Python** — core language
- **FastMCP** — MCP server framework, handles protocol/tool registration
- **SQLite** — lightweight database for inventory and sales history
- **scikit-learn** — linear regression for demand forecasting
- **pandas / numpy** — data handling (used indirectly via scikit-learn)

## Architecture & design reasoning

- **One regression model per item, not one shared model.** Different items (e.g. Chicken vs Rice) have different demand patterns; a single shared model risks averaging across products instead of learning item-specific behavior.
- **`is_weekend` (binary) as the feature, not raw day-of-week.** Early testing showed that with a step-function demand pattern (flat weekdays, boosted weekends), a binary weekend flag fits the data more accurately than a continuous day-of-week feature, which forces an unrealistic smooth trend across all 7 days. This was verified empirically by comparing predictions against known historical averages.
- **ISO date format (`YYYY-MM-DD`) used throughout.** This format sorts correctly under plain string comparison (`<=`, `>=`), so date-range queries in SQL don't require special date parsing.
- **Parameterized SQL queries everywhere.** All queries use `?` placeholders rather than string interpolation, to prevent SQL injection — especially relevant here since MCP tool arguments are effectively untrusted external input, similar to a public API endpoint.
- **`recommend_order` treats waste-risk as informational, not a math adjustment.** Underordering (stockout) is treated as a worse failure mode for a restaurant than slight overstock, so waste-risk items are still ordered based on full predicted demand, with waste-risk surfaced as a separate flag for the manager to act on manually. This is a deliberate V1 simplification pending real manager feedback (see Future Work).

## Why MCP instead of a traditional REST API?

A standard REST API requires the client to have **hardcoded knowledge** of every endpoint — a developer has to read documentation, know exactly which URL does what, and write specific code to call it. The client and server are tightly coupled to a fixed, pre-agreed contract.

MCP inverts this. Instead of exposing fixed endpoints, the server exposes a set of **self-describing tools** — each with a name, a natural-language description, and a typed schema — that an AI agent can discover and reason about at runtime. The agent decides *which* tool to call and *how* to call it, based on a user's natural-language intent, without the developer writing any glue code to map "user requests" to "specific endpoints."

Concretely, for this project: a restaurant manager can ask Claude *"what should I order this week?"* — Claude reads the available tool descriptions, recognizes `recommend_order` is relevant, calls it with the right arguments, and turns the structured JSON response into a plain-language answer. With a REST API, this same interaction would require a separate NLU/intent-routing layer built specifically to map phrases to endpoints — MCP gets this "for free," because the AI model itself handles that reasoning step.

This matters most in domains like restaurant operations, where the end user (a manager, not a developer) shouldn't need to learn an API or a specific UI — they should be able to just *ask*, in whatever words come naturally, and have the right tool get called.

## Business & growth potential

This MCP-first architecture is designed to scale in a few concrete directions:

- **New data sources plug in as new tools, not new UI screens.** Adding weather data, local event calendars, or holiday effects (planned for MISE) means adding new tools or enriching existing ones — any MCP client automatically gains access to the new capability without a redesign.
- **Multi-restaurant / multi-tenant scaling.** The same tool interface (`get_inventory`, `predict_demand`, etc.) could be parameterized by restaurant/location ID, letting a single MCP server support a chain rather than one location — the tool contract doesn't need to change, just the underlying data scope.
- **Any MCP-compatible client benefits, not just one app.** Because tools are exposed via a standard protocol rather than a bespoke API, any current or future MCP client (Claude Desktop, custom internal tools, third-party agents) can integrate with zero additional backend work — the investment in building good tools compounds across every future client, rather than being locked to one frontend.
- **Staffing, procurement, and supplier integrations** are natural next tools to add (e.g. `recommend_staffing_levels`, `check_supplier_pricing`) — each one is additive, not a rearchitecture, because the MCP tool model is built for incremental capability growth.
- **Long-term vision (MISE):** this V1 backend is the technical seed for a broader Restaurant Intelligence Engine — incorporating weather, holidays, events, and richer operational data into the same tool-based architecture, so growth is a matter of adding smarter tools on a proven foundation, not rebuilding from scratch.

## Known limitations (honest V1 scope)

- **Synthetic training data.** Sales history is randomly generated per item (14 days, weekday/weekend pattern), not real restaurant data. This was a deliberate choice to have full control over a known, verifiable pattern for validating the model — but predictions are only as good as this synthetic pattern, not real-world demand signals like weather, holidays, or local events.
- **Small training set.** 14 data points per item is enough to prove the mechanism works, but far below what a production forecasting model would need for robustness.
- **No model persistence.** Every call to `predict_demand()` retrains a fresh model from scratch. Fine for this dataset size, but wasteful at scale.
- **Flat waste-risk threshold.** A single fixed 3-day window, rather than tiered urgency buckets (24hr/weekly/monthly), which would better reflect real restaurant purchasing cycles.
- **No frontend yet.** Pure backend MCP server — a frontend is planned as the next phase, not part of V1.

## Setup

```powershell
git clone https://github.com/hettrivedi18/FoodManagerEngine.git
cd FoodManagerEngine
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python database.py      # initializes and seeds the SQLite database
python server.py        # starts the MCP server (stdio transport)
```

To test the tools directly without a full MCP client setup, see `test_client.py`.

## Roadmap

See [`FUTURE_WORK.md`](./FUTURE_WORK.md) for planned V1.1+/V2 improvements, including tiered waste-risk logic, model persistence, order-cycle-aware recommendations, and the long-term vision of evolving this into **MISE — Restaurant Intelligence Engine**.