# S/4HANA Procurement Agent

Sample AI agent connected to SAP S/4HANA On-Premise and BTP

## Business challenge

A Procurement Manager spends significant time (up to 10 minutes per lookup) manually searching for purchase order status in SAP S/4HANA. The goal is to provide a conversational AI agent that allows the manager to query purchase order data — including status, vendor, and amounts — using natural language, dramatically reducing lookup time.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time to look up PO status | 10 minutes | < 1 minute | 1 month | Purchase Order Management (Source to Pay) | user |

## Key Milestones

1. **API connectivity established** — Agent successfully connects to S/4HANA On-Premise via SAP BTP Business Connector and retrieves live PO data.
2. **MCP tool integration** — MCP translation file generated and validated for the Purchase Order OData API; agent can invoke it as a tool.
3. **Natural language query handling** — Agent correctly interprets and responds to procurement questions (e.g. "Show me open POs for vendor X above €50,000").
4. **Agent deployed on BTP** — Agent is live and accessible to the Procurement Manager via the designated interface.

## Business Architecture (RBA)

### End-to-End Process

Source to Pay (generic)

### Process Hierarchy

```
Source to Pay (E2E)
└── Procure to Receipt (generic)
    └── Purchase products and services (BPS-329)
        └── Manage purchase order
└── Invoice to Pay (generic)
    └── Process supplier invoices (BPS-325)
        └── Receive and process supplier invoices
└── Source to Contract (generic)
    └── Manage procurement contracts (BPS-328)
        └── Manage procurement contracts
```

### Summary

The agent addresses the Procure to Receipt phase of Source to Pay, specifically the "Manage purchase order" activity. The primary focus is on PO status lookup and analysis in SAP S/4HANA On-Premise, with invoices and contracts available as secondary scope.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
| ---------------------- | ----------------------- | ---------- | ----------------- | ------------------ | ------------------ | ------------------- | ---- | ------------------- |
| Query purchase order status, vendor, amount | SAP S/4HANA – Purchase Order Processing (SC5215 / SC416) | `sap.s4:apiResource:API_PURCHASEORDER_PROCESS_SRV:v1` | — | — | — | — | Yes | No pre-built MCP server; MCP translation file must be generated from OData spec |
| Query supplier invoices | SAP S/4HANA – Supplier Invoice Processing (SC312 / SC5729) | `sap.s4:apiResource:API_SUPPLIERINVOICE_PROCESS_SRV:v1` | — | — | — | — | Maybe | In scope if user requests invoice queries; same pattern as PO |
| Query procurement contracts | SAP S/4HANA – Procurement Contract Management (SC354 / SC5019) | `sap.s4:apiResource:API_PURCHASECONTRACT_PROCESS_SRV_0002:v1` | — | — | — | — | Maybe | In scope if user requests contract queries |

### Key findings

- SAP S/4HANA On-Premise covers all three procurement sub-processes natively through standard OData APIs.
- No pre-built MCP server exists for the relevant procurement APIs; MCP translation files must be generated during the specification phase.
- The `API_PURCHASEORDER_PROCESS_SRV` OData API is the primary integration point and will be the first tool surfaced to the agent.
- BTP Business Connector will serve as the secure bridge between BTP (where the agent runs) and S/4HANA On-Premise.
- APIs marked `unavailable: true` in the discovery results (e.g. `OP_API_PURCHASECONTRACT_PROCESS_SRV`) are excluded from the solution design.
- The solution requires no n8n workflow; a pure AI Agent pattern is sufficient for this conversational query use case.

## Recommendations

### S/4HANA Procurement AI Agent

#### Executive Summary

Pro-code Python agent on BTP with S/4HANA OData API integration

#### Recommended Solution

A Python-based AI agent (A2A protocol) deployed on SAP BTP that uses the SAP S/4HANA On-Premise Purchase Order OData API as its primary data source. The agent is exposed via the A2A endpoint and connects to S/4HANA through the BTP Business Connector. An MCP translation file is generated from the OData specification to expose PO query capabilities as structured tools. The agent responds to natural language questions from the Procurement Manager.

#### Problem Statement

Procurement Managers spend up to 10 minutes per lookup manually navigating SAP S/4HANA to check purchase order status. This creates delays in decision-making and reduces productivity across daily procurement operations.

#### Affected User Roles

- Procurement / Purchasing Manager

#### Important factors

##### Reduces manual lookup time through conversational access

The agent allows users to ask questions like "What is the status of PO 4500001234?" or "Show me all open POs for vendor ABC" and receive instant answers, eliminating manual navigation.

##### Secure connectivity via BTP Business Connector

The agent leverages SAP BTP's secure connectivity to S/4HANA On-Premise — no direct RFC or custom middleware required.

#### Potential risks

##### API availability on On-Premise system

The OData services must be active and accessible on the S/4HANA On-Premise system. This should be verified during setup.

##### Data volume and query performance

Large PO datasets may require filtering parameters to be enforced in the agent's tool calls to avoid slow responses.

#### Recommended solution category

AI Agent

#### Intent fit
90%
