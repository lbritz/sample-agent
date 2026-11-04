# Product Requirements Document (PRD)

**Title:** S/4HANA Procurement Agent  
**Date:** 2026-10-30  
**Owner:** Procurement Team  
**Solution Category:** AI Agent

---

## Product Purpose & Value Proposition

**Elevator Pitch:**
Procurement Managers waste up to 10 minutes per lookup manually navigating SAP S/4HANA to check purchase order status. This agent lets them ask plain-language questions and get instant, accurate answers — no more clicking through SAP menus.

**Business Need:**
The procurement team handles a high volume of daily purchase order queries — checking status, verifying vendors, reviewing amounts. Today this requires manual navigation of the SAP S/4HANA interface, which is time-consuming and interrupts higher-value work. A conversational AI agent removes this friction by connecting directly to live S/4HANA data and answering queries on demand.

**Expected Value:**
- Reduce PO status lookup time from 10 minutes to under 1 minute
- Free up Procurement Manager capacity for strategic sourcing activities
- Provide a reusable, extensible agent foundation for future procurement scenarios (invoices, contracts)

**Product Objectives (Prioritized):**
1. Deliver instant, accurate responses to natural language PO queries using live S/4HANA data
2. Establish secure, reliable connectivity between the BTP-hosted agent and S/4HANA On-Premise
3. Provide a well-instrumented, extensible agent that can be expanded to cover invoices and contracts in future iterations

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time to look up PO status | 10 minutes | < 1 minute | 1 month | Purchase Order Management (Source to Pay) | user |

**Notes:** The baseline and target reflect the Procurement Manager's daily PO query workflow. Success is measured by elapsed time from question to answer, including agent response time.

---

## User Profiles & Personas

### Primary Persona: Alex Chen — Procurement Manager

Alex is a 34-year-old Procurement Manager at a mid-sized manufacturing company running SAP S/4HANA On-Premise. He manages a portfolio of 200+ active purchase orders at any given time, spanning multiple vendors and categories. His day involves frequent status checks — a vendor calls asking about payment, a colleague needs a delivery estimate, his manager wants a spend summary. Each query currently means logging into SAP, navigating to the correct transaction, and manually filtering results. He's confident with SAP but frustrated by how long routine lookups take. He values speed, accuracy, and reliability above all else. A new tool that gives wrong answers is worse than no tool at all.

**Goals:**
- Get instant answers to PO status questions without navigating SAP manually
- Quickly identify overdue or blocked purchase orders
- Respond to vendor and stakeholder queries faster

**Key Tasks:**
- Ask "What is the status of PO 4500001234?" and get an instant structured answer
- Request a list of all open POs for a specific vendor
- Filter POs by amount threshold (e.g. "show me all POs above €50,000 still open")
- Get a summary of all open POs for his current week

### Other User Types

- **IT / BTP Administrator**: responsible for deploying and maintaining the agent on SAP BTP, managing the BTP Business Connector configuration to S/4HANA On-Premise.

---

## User Goals & Tasks

### For Alex Chen (Procurement Manager):

**Goals:**
- Reduce time spent on routine PO status lookups to under 1 minute
- Get reliable, up-to-date answers directly from the live S/4HANA system

**Key Tasks:**
- Query a single PO by number and receive status, vendor, amount, and delivery date
- List open POs filtered by vendor name or vendor number
- List open POs above a specified monetary threshold
- Ask for a high-level summary of all open POs

---

## Product Principles

1. **Accuracy over speed**: The agent must only return data from the live S/4HANA system. It must never fabricate or estimate procurement data.
2. **Read-only by default**: The agent has no write access to S/4HANA. It queries data; it never creates, updates, or deletes records.
3. **Transparent sourcing**: Every answer must be traceable to the underlying OData API response. The agent should cite the PO number and data fields it is drawing from.
4. **Fail safely**: If the agent cannot retrieve data (connectivity issue, API error, insufficient permissions), it must clearly communicate the failure — never silently return empty or partial results as if they were complete.

---

## Business Context

**Current State:**
Procurement Managers use the SAP S/4HANA On-Premise interface (transactions ME23N, ME2M, and similar) for purchase order lookups. Each query requires manual navigation, transaction selection, and filter input — a process that takes 5–10 minutes per lookup. For a manager handling dozens of queries per day, this represents a significant productivity drain.

**Strategic Alignment:**
This agent is a first step in building an AI-enabled procurement capability on SAP BTP. It demonstrates the value of conversational access to ERP data and establishes reusable integration patterns (BTP Business Connector, MCP tool generation) that can be applied to invoices, contracts, and other procurement scenarios.

**Success Criteria:**
See the Business Metrics section above.

---

## Goals and Non-Goals

### Goals (In Scope)

- Natural language querying of purchase order data from SAP S/4HANA On-Premise
- Filtering POs by vendor, status, and amount
- Summarizing open purchase orders
- Secure connectivity to S/4HANA via SAP BTP Business Connector
- Extensible agent architecture ready for future tool additions (invoices, contracts)

### Non-Goals (Out of Scope)

- Creating, modifying, or cancelling purchase orders
- Querying supplier invoice or contract data (planned for future iterations)
- Integration with systems other than SAP S/4HANA (e.g. Ariba, Business Network)
- UI or web application — the agent is accessed via its A2A endpoint
- SAP Ariba or Business Network integration

---

## Requirements

### Must-Have Requirements

**REQ-001**: Query a single purchase order by number

- **Problem to Solve**: A Procurement Manager needs to look up the status of a specific PO without navigating SAP manually.
- **User Story**: As a Procurement Manager, I need to ask for a specific PO by number so that I can immediately see its status, vendor, total amount, and expected delivery date.
- **Acceptance Criteria**:
  - Given a valid PO number, when I ask "What is the status of PO 4500001234?", then the agent returns PO status, vendor name, net order value, and delivery date within 10 seconds.
  - Given an invalid PO number, then the agent informs me that the PO was not found.
- **Maps to Objective**: Objective 1 — instant, accurate PO query responses
- **Priority Rank**: 1

**REQ-002**: List open purchase orders by vendor

- **Problem to Solve**: Procurement Managers frequently need to review all outstanding POs for a given vendor — for payment queries or delivery follow-up.
- **User Story**: As a Procurement Manager, I need to ask for all open POs for a specific vendor so that I can quickly review outstanding commitments with that supplier.
- **Acceptance Criteria**:
  - Given a vendor name or number, when I ask "Show me all open POs for vendor Acme Corp", then the agent returns a list of open POs with their amounts and statuses.
  - Given a vendor with no open POs, then the agent responds clearly with "No open POs found for that vendor."
- **Maps to Objective**: Objective 1
- **Priority Rank**: 2

**REQ-003**: Filter purchase orders by amount threshold

- **Problem to Solve**: Managers need to identify high-value open POs for prioritization and approval oversight.
- **User Story**: As a Procurement Manager, I need to filter open POs above a specified amount so that I can focus on high-value commitments.
- **Acceptance Criteria**:
  - Given an amount threshold, when I ask "Show me open POs above €50,000", then the agent returns matching POs sorted by value descending.
- **Maps to Objective**: Objective 1
- **Priority Rank**: 3

**REQ-004**: Summarize all open purchase orders

- **Problem to Solve**: Procurement Managers need a quick overview of the current open PO landscape for reporting and planning.
- **User Story**: As a Procurement Manager, I need to ask for a summary of all open POs so that I can understand the current procurement workload at a glance.
- **Acceptance Criteria**:
  - When I ask "Give me a summary of all open POs", then the agent returns the total count and total net value of open POs.
- **Maps to Objective**: Objective 1
- **Priority Rank**: 4

**REQ-005**: Secure connectivity to SAP S/4HANA On-Premise

- **Problem to Solve**: The agent runs on SAP BTP and must access data from an on-premise S/4HANA system securely without exposing the ERP system to the public internet.
- **User Story**: As an IT Administrator, I need the agent to connect to S/4HANA via the BTP Business Connector so that data is accessed securely without opening firewall rules.
- **Acceptance Criteria**:
  - The agent retrieves PO data exclusively through the BTP Business Connector — no direct internet exposure of the on-premise system.
  - Connection failures are surfaced to the user as a clear error message, not silently swallowed.
- **Maps to Objective**: Objective 2 — secure, reliable connectivity
- **Priority Rank**: 5

### High-Want Requirements

**REQ-006**: Graceful handling of ambiguous queries

- **Problem to Solve**: Users may phrase questions in unexpected ways; the agent should guide them rather than fail silently.
- **User Story**: As a Procurement Manager, I need the agent to ask for clarification when my query is ambiguous so that I still get a useful answer.
- **Priority Rank**: 1

**REQ-007**: Response includes a direct reference to the source data

- **Problem to Solve**: Managers need confidence that answers reflect live ERP data, not cached or estimated values.
- **User Story**: As a Procurement Manager, I need the agent to indicate that data comes directly from S/4HANA so that I can trust the answer.
- **Priority Rank**: 2

### Nice-to-Have Requirements

**REQ-008**: Extensibility for invoice queries

- **Problem to Solve**: Supplier invoice queries follow the same pattern as PO queries and could be handled by the same agent with an additional tool.
- **Priority Rank**: 1

**REQ-009**: Extensibility for contract queries

- **Problem to Solve**: Contract status and expiry questions are a natural complement to PO queries for a Procurement Manager.
- **Priority Rank**: 2

---

## Non-Functional Requirements

### Performance

- **Latency**: Agent response to a PO query must be returned within 10 seconds (end-to-end, including OData API call).
- **Throughput**: The agent must handle at least 20 concurrent queries without degradation.

### Reliability

- **Availability**: The agent must be available during business hours with 99% uptime.
- **Fallback**: If the S/4HANA OData API is unreachable, the agent must return a clear error message: "I was unable to retrieve data from S/4HANA at this time. Please try again shortly."

### Explainability

- **Traceability**: Every PO data point returned by the agent is sourced from the OData API response — no data is inferred or estimated.
- **Decision Logging**: All tool invocations (MCP calls to the PO API) are logged with input parameters and response status.
- **Uncertainty Communication**: If the API returns partial results due to paging or timeout, the agent must disclose this to the user.

---

## Solution Architecture

**Architecture Overview:**
The agent runs as a Python A2A service on SAP BTP. It receives natural language queries, determines the appropriate OData operation, and invokes the S/4HANA Purchase Order API via a generated MCP translation file. Connectivity to the on-premise S/4HANA system is managed through the SAP BTP Business Connector (Cloud Connector).

**Key Components:**

- **Python AI Agent (A2A)**: Core agent logic, intent interpretation, and response generation. Deployed on SAP BTP.
- **MCP Translation File**: Generated from the `API_PURCHASEORDER_PROCESS_SRV` OData specification. Exposes PO query operations as structured tools the agent can call.
- **SAP BTP Business Connector (Cloud Connector)**: Secure tunnel between SAP BTP and the on-premise S/4HANA system. No public internet exposure of the ERP.
- **SAP S/4HANA On-Premise (OData API)**: Source of truth for all purchase order data. Accessed via `API_PURCHASEORDER_PROCESS_SRV`.

**Integration Points:**

- **S/4HANA ↔ BTP**: Read-only OData calls via BTP Business Connector; triggered per user query; no data is cached on the BTP side.

**Deployment Environments:**

- **Development**: BTP subaccount with sandbox S/4HANA connectivity for testing.
- **Production**: BTP subaccount connected to the live S/4HANA On-Premise system via the production Cloud Connector.

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
The agent is designed with a tool-registry pattern. The initial release includes one MCP tool (Purchase Order API). Additional tools — for supplier invoices (`API_SUPPLIERINVOICE_PROCESS_SRV`) and procurement contracts (`API_PURCHASECONTRACT_PROCESS_SRV_0002`) — can be added in future iterations without changing the agent's core logic. Extension hooks are documented for the IT Administrator persona.

**Business Step Instrumentation:**
All four key milestones are instrumented as business steps using structured log statements. Log statements follow the pattern: `[MILESTONE_ID].[achieved|missed]: [description]`. This enables production monitoring and debugging of agent behavior.

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent — the agent independently decides which OData filters to apply based on the natural language query, without a fixed workflow graph.

**Actions the system performs without human approval:**
- Query purchase order data from S/4HANA OData API (read-only)
- Filter, format, and return PO results to the user

**Actions that require human review or approval:**
- None — the agent is read-only. No write operations are performed.

**Model or engine used:** SAP Generative AI Hub (LLM for intent interpretation and response generation)

**Knowledge & data sources accessed:**
- SAP S/4HANA On-Premise — `API_PURCHASEORDER_PROCESS_SRV` OData API — purchase order master and status data; stewardship owned by the Procurement team.

**Tools or connectors invoked:**
- **Purchase Order MCP Tool** (read-only): Queries PO data from S/4HANA. Operations include: get PO by number, list POs by vendor, list POs by status, filter POs by amount. No side effects — strictly read-only.

**Guardrails & fail-safes:**
- The agent must never attempt write operations (POST, PUT, PATCH, DELETE) against any SAP system.
- If the OData API returns an error or empty result, the agent must communicate this clearly rather than returning a fabricated answer.
- If the user's query cannot be mapped to a supported PO query, the agent must respond with a clarification prompt rather than guessing.
- Queries must always include at least one filter parameter — unbounded reads over the full PO dataset are prohibited to protect system performance.

---

## Milestones

### M1: API Connectivity Established

- **Description**: The agent successfully connects to SAP S/4HANA On-Premise via the BTP Business Connector and retrieves live purchase order data.
- **Achieved when**: A test query returns at least one PO record from the live S/4HANA system without error.
- **Log on achievement**: `M1.achieved: S/4HANA OData API connectivity verified — live PO data retrieved successfully`
- **Log on miss**: `M1.missed: S/4HANA OData API connectivity could not be established — check BTP Business Connector configuration`

### M2: MCP Tool Integration Complete

- **Description**: The MCP translation file for `API_PURCHASEORDER_PROCESS_SRV` is generated, validated, and the agent can invoke it as a structured tool.
- **Achieved when**: The agent successfully invokes the Purchase Order MCP tool and receives a valid OData response.
- **Log on achievement**: `M2.achieved: MCP tool for Purchase Order API registered and invocation successful`
- **Log on miss**: `M2.missed: MCP tool invocation failed — verify translation file and tool registration`

### M3: Natural Language Query Handling

- **Description**: The agent correctly interprets and responds to procurement questions in natural language, applying appropriate OData filters.
- **Achieved when**: The agent correctly handles the four core query types (single PO lookup, vendor filter, amount filter, open PO summary) with accurate results.
- **Log on achievement**: `M3.achieved: Natural language PO query resolved — intent classified and OData filters applied correctly`
- **Log on miss**: `M3.missed: Natural language query could not be resolved — intent classification or filter mapping failed`

### M4: Agent Deployed on BTP

- **Description**: The agent is live on SAP BTP and accessible to the Procurement Manager via the designated interface.
- **Achieved when**: The A2A endpoint is reachable, authenticated, and returns correct responses in the production environment.
- **Log on achievement**: `M4.achieved: Agent deployed and accessible on SAP BTP — production endpoint verified`
- **Log on miss**: `M4.missed: Agent deployment incomplete — check BTP service bindings and runtime configuration`

---

## Risks, Assumptions, and Dependencies

### Risks

- **OData service activation**: The `API_PURCHASEORDER_PROCESS_SRV` OData service must be active and accessible on the S/4HANA On-Premise system. If not activated, API connectivity (M1) will fail.
- **Query performance on large datasets**: Without mandatory filter parameters, queries over large PO datasets may time out. The guardrail requiring at least one filter per query mitigates this risk.
- **LLM intent accuracy**: The agent relies on an LLM to interpret natural language and map it to OData filter parameters. Edge-case phrasings may result in incorrect filters. Covered by the clarification guardrail (REQ-006).

### Assumptions (Validate These)

- The BTP Business Connector (Cloud Connector) is already installed and configured in the customer's landscape.
- The IT Administrator has the necessary S/4HANA authorizations to activate and expose the `API_PURCHASEORDER_PROCESS_SRV` OData service.
- The Procurement Manager's queries will be in scope for read-only PO data — no approval or write-back workflows are expected in this release.

### Dependencies

- **SAP BTP subaccount** with SAP AI Core / Generative AI Hub service plan enabled.
- **SAP BTP Business Connector (Cloud Connector)** configured and connected to the S/4HANA On-Premise system.
- **S/4HANA On-Premise OData service** `API_PURCHASEORDER_PROCESS_SRV` activated and authorized for the service account used by the agent.

---

## Appendix

### Glossary

- **A2A (Agent-to-Agent protocol)**: The communication protocol used by the Python agent to expose its capabilities as an AI service on SAP BTP.
- **MCP (Model Context Protocol)**: A protocol that exposes API operations as structured tools an AI agent can discover and invoke.
- **MCP Translation File**: A generated artifact that maps OData service operations to MCP tool definitions, enabling the agent to call S/4HANA APIs as tools.
- **BTP Business Connector (Cloud Connector)**: An on-premise component of SAP BTP that creates a secure tunnel between SAP BTP and on-premise SAP systems, without requiring inbound firewall rules.
- **OData**: An open protocol for querying and updating data, used by SAP S/4HANA to expose ERP data via RESTful APIs.

### References

- SAP S/4HANA Purchase Order OData API: `API_PURCHASEORDER_PROCESS_SRV` — SAP Business Accelerator Hub
- SAP BTP Business Connector (Cloud Connector) documentation — SAP Help Portal
- SAP AI Core / Generative AI Hub — SAP BTP Service Catalog
- SAP A2A Agent Protocol documentation
