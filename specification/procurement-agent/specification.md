# Specification: procurement-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Data Dependencies

- No Data Product ORD IDs — agent integrates directly with S/4HANA OData API via MCP tool (Path A).

## API Integration

- API Name: Purchase Order
- API ORD ID: `sap.s4:apiResource:API_PURCHASEORDER_PROCESS_SRV:v1`
- API Type: OData
- Spec file: `specification/procurement-agent/api-specs/API_PURCHASEORDER_PROCESS_SRV.edmx`

MCP API: sap.s4:apiResource:API_PURCHASEORDER_PROCESS_SRV:v1
MCP tool scope: read-only
Resources in scope: A_PurchaseOrder, A_PurchaseOrderItem

---

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` to understand business requirements
- [x] Bootstrap agent code in `assets/procurement-agent/` using the `sap-agent-bootstrap` instructions from the agent skill (invoke from inside `assets/procurement-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

> Read [guidelines-agent-skills.md](../guidelines-agent-skills.md) before proceeding.

No runtime skills are required for this agent. The purchase order query logic is straightforward enough to be handled entirely within the system prompt and MCP tools without a separate task-specific skill file.

---

## Project-Specific Tasks

### Agent Identity & System Prompt

- [x] Set the agent name to `S/4HANA Procurement Agent` and description to `Answers natural language questions about purchase orders from SAP S/4HANA`
- [x] Open `assets/procurement-agent/app/agent.py` and update the `@prompt_section` system prompt to include:
  - The agent's role: a procurement assistant that answers questions about purchase orders using live SAP S/4HANA data
  - Instruction: "You MUST use tools to retrieve live data from SAP S/4HANA. Never fabricate, guess, or invent procurement data."
  - Instruction: "When calling tools that support pagination, always set the page size parameter (top, limit, pageSize) to a maximum of 100 items to prevent context overflow. Inform the user when this limit is applied."
  - Instruction: "If a tool returns an error, report the error message exactly as received. Do not suggest workarounds or alternative approaches unless asked."
  - Instruction: "All data returned is read-only. You cannot create, update, or cancel purchase orders."
  - Instruction: "Always include at least one filter parameter in every purchase order query (e.g. PO number, vendor, status, or amount threshold). Do not perform unbounded reads over the full PO dataset."
  - Instruction: "If the user's query is ambiguous or cannot be mapped to a supported filter, ask for clarification before invoking any tool."

### Core Query Capabilities

- [x] **REQ-001 — Single PO lookup by number**: Ensure the agent system prompt instructs it to query a purchase order by its exact PO number (`PurchaseOrder` key field). The response must include: PO number, status (`PurchaseOrderStatus`), vendor (`Supplier`), net order value (`NetPriceAmount` / `NetOrderValue`), and delivery date from the PO item (`ScheduleLine` or `DeliveryDate`). If the PO is not found, the agent must clearly say so — never return empty results silently.
- [x] **REQ-002 — List open POs by vendor**: Ensure the agent can filter POs by `Supplier` field and restrict to open status (e.g. `PurchaseOrderStatus ne 'L'`). Response must list PO numbers, amounts, and statuses.
- [x] **REQ-003 — Filter POs by amount threshold**: Ensure the agent can apply a numeric filter on net order value to return POs above a specified amount. Results must be presented in descending order by value.
- [x] **REQ-004 — Open PO summary**: Ensure the agent can retrieve and count open purchase orders, presenting the total count and sum of net values. Enforce the 100-item page size limit and notify the user if results are paginated.

### Error Handling & Guardrails

- [x] Add system prompt instruction: "If the SAP S/4HANA API is unreachable or returns an error, respond with: 'I was unable to retrieve data from S/4HANA at this time. Please try again shortly.' Do not attempt to answer the question from memory or make up data."
- [x] Add system prompt instruction: "You have read-only access. Never attempt to create, modify, or delete any purchase order or related document."
- [x] Add system prompt instruction: "Every query must include at least one explicit filter. If the user asks for 'all purchase orders' without any qualifier, ask them to specify a vendor, status, date range, or amount threshold."

---

## Business Instrumentation

- [x] Implement business step instrumentation for all four milestones from the PRD using structured logging (`[MILESTONE_ID].[achieved|missed]: [description]`) and OpenTelemetry custom spans:
  - **M1** — S/4HANA OData API connectivity: log `M1.achieved: S/4HANA OData API connectivity verified — live PO data retrieved successfully` / `M1.missed: S/4HANA OData API connectivity could not be established — check BTP Business Connector configuration`
  - **M2** — MCP tool integration: log `M2.achieved: MCP tool for Purchase Order API registered and invocation successful` / `M2.missed: MCP tool invocation failed — verify translation file and tool registration`
  - **M3** — Natural language query resolved: log `M3.achieved: Natural language PO query resolved — intent classified and OData filters applied correctly` / `M3.missed: Natural language query could not be resolved — intent classification or filter mapping failed`
  - **M4** — Agent deployed: log `M4.achieved: Agent deployed and accessible on SAP BTP — production endpoint verified` / `M4.missed: Agent deployment incomplete — check BTP service bindings and runtime configuration`
- [x] See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python-specific OpenTelemetry span implementation
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

> Read [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — Path A applies (OData spec present, no existing MCP server).

- [x] Verify `specification/procurement-agent/api-specs/API_PURCHASEORDER_PROCESS_SRV.edmx` exists and is non-empty
- [x] Invoke the `mcp-translation-file` skill with the downloaded EDMX spec at `specification/procurement-agent/api-specs/API_PURCHASEORDER_PROCESS_SRV.edmx` and API ORD ID `sap.s4:apiResource:API_PURCHASEORDER_PROCESS_SRV:v1` to generate the MCP translation file
  - MCP tool scope: read-only
  - Resources in scope: `A_PurchaseOrder`, `A_PurchaseOrderItem`
- [x] After `mcp-translation-file` completes, invoke the `setup-solution` skill to create and register the MCP server asset for the generated translation file
- [x] Read the generated MCP server asset's `asset.yaml` and copy the exact `ordId` value for use in the agent's `requires` entry:
  ```bash
  grep '^ordId:' assets/<mcp-server-asset-name>/asset.yaml
  ```
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module — see [guidelines-agent-python.md](../guidelines-agent-python.md) for the canonical pattern. NEVER import directly from `sap_cloud_sdk.agentgateway`. NEVER create direct HTTP clients.
- [x] Add the MCP server dependency to `assets/procurement-agent/asset.yaml` under `requires`:
  ```yaml
  requires:
    - name: <mcp-server-asset-name>
      kind: mcp-server
      ordId: <exact-ordId-from-generated-asset-yaml>
  ```
- [x] Generate `mcp-mock.json` using the `mcp-mock-config` skill after MCP translation and setup-solution complete

---

## Testing

> See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python testing setup and patterns.

- [x] `conftest.py` only sets `IBD_TESTING=true` — this causes the agent to run with mock MCP tool results during tests
- [x] Write unit tests in `assets/procurement-agent/tests/` covering:
  - Single PO lookup by number (REQ-001) — mock returns a valid PO; assert all key fields are present in response
  - Single PO lookup — mock returns empty; assert agent responds with "not found" message
  - Vendor filter query (REQ-002) — mock returns list of open POs; assert list is returned correctly
  - Amount threshold filter (REQ-003) — mock returns filtered POs; assert ordering and fields
  - Open PO summary (REQ-004) — mock returns paginated result; assert count and total value are reported
  - Error scenario — mock returns API error; assert agent relays the error message verbatim
- [x] Write one integration test executing end-to-end agent flow by calling the agent's `invoke` function with mocked LLM responses and mocked external systems (tests must run offline)
- [x] Run `pytest` from `assets/procurement-agent/` (no args) — if coverage < 70%, add tests until threshold met
- [x] Run `pytest` again from `assets/procurement-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/procurement-agent/`
