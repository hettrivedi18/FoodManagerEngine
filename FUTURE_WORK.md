# Future Improvements (V1.1+)

- **Tiered waste-risk buckets**: instead of a single fixed threshold (e.g. 3 days),
  group items into urgency tiers (24hr, weekly, bi-weekly, monthly, 6-monthly)
  with tier-specific business logic for reordering/discounting strategy.

- **Multi-agent verification layer for AI-generated insights**: as data volume grows
  (more items, longer history, multiple locations), a single LLM pass generating
  natural-language insights risks hallucinating patterns that aren't actually present
  in the data. Add a verification step where any claim an LLM makes about the data
  (e.g. "demand was under-predicted by X% on weekends") is checked against a
  deterministic, code-based tool (not another LLM guess) before being surfaced to
  the manager. Natural fit for MCP: expose a `verify_prediction_claim()` tool that
  the analysis agent must call before presenting any specific numeric claim.
