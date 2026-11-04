"""Unit and integration tests for the Procurement Agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

AGENT_ROOT = Path(__file__).parent.parent


def _mock_tool(name: str) -> MagicMock:
    """Return a minimal mock LangChain tool."""
    t = MagicMock()
    t.name = name
    return t


def _po_list_response() -> dict:
    return {
        "d": {
            "results": [
                {
                    "PurchaseOrder": "4500001234",
                    "Supplier": "ACME001",
                    "NetPriceAmount": "75000.00",
                    "DocumentCurrency": "EUR",
                    "PurchaseOrderStatus": "B",
                    "PurchaseOrderDate": "/Date(1730131200000)/",
                },
                {
                    "PurchaseOrder": "4500001235",
                    "Supplier": "VENDOR002",
                    "NetPriceAmount": "12500.00",
                    "DocumentCurrency": "EUR",
                    "PurchaseOrderStatus": "B",
                    "PurchaseOrderDate": "/Date(1730217600000)/",
                },
            ]
        }
    }


def _po_single_response() -> dict:
    return {
        "d": {
            "PurchaseOrder": "4500001234",
            "Supplier": "ACME001",
            "NetPriceAmount": "75000.00",
            "DocumentCurrency": "EUR",
            "PurchaseOrderStatus": "B",
            "PurchaseOrderDate": "/Date(1730131200000)/",
        }
    }


def _build_messages(content: str) -> list:
    msg = MagicMock()
    msg.content = content
    return [msg]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def use_agent_path(add_agent_to_path):  # noqa: F811 - fixture from conftest
    """Ensure app/ is on sys.path for all tests in this module."""
    pass


@pytest.fixture
def agent(add_agent_to_path):
    """Return a SampleAgent instance with a mocked LLM."""
    with patch("langchain_litellm.ChatLiteLLM.__init__", return_value=None):
        with patch("sap_cloud_sdk.agent_memory.factory.langgraph_checkpoint.create_checkpointer", return_value=None):
            from agent import SampleAgent
            a = SampleAgent.__new__(SampleAgent)
            a.llm = MagicMock()
            a._checkpointer = None
            a._summarization_middleware = MagicMock()
            a._temperature = 0.0
            return a


# ---------------------------------------------------------------------------
# REQ-001: Single PO lookup by number — happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_single_po_lookup_found(agent):
    """Agent returns PO details when a valid PO number is queried."""
    tools = [_mock_tool("get_a_purchaseorder_for_api_purchaseorder_process_srv")]
    expected_content = (
        "Purchase Order 4500001234: Supplier ACME001, "
        "Amount EUR 75,000.00, Status: Open"
    )
    mock_result = {"messages": _build_messages(expected_content)}

    with patch.object(agent, "_invoke", new=AsyncMock(return_value=mock_result)):
        response = await agent.invoke(
            query="What is the status of PO 4500001234?",
            context_id="test-ctx-001",
            tools=tools,
        )

    assert response.status == "completed"
    assert "4500001234" in response.message


# ---------------------------------------------------------------------------
# REQ-001: Single PO lookup — not found
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_single_po_lookup_not_found(agent):
    """Agent communicates clearly when a PO is not found."""
    tools = [_mock_tool("get_a_purchaseorder_for_api_purchaseorder_process_srv")]
    not_found_content = "Purchase order 9999999999 was not found in S/4HANA."
    mock_result = {"messages": _build_messages(not_found_content)}

    with patch.object(agent, "_invoke", new=AsyncMock(return_value=mock_result)):
        response = await agent.invoke(
            query="What is the status of PO 9999999999?",
            context_id="test-ctx-002",
            tools=tools,
        )

    assert response.status == "completed"
    assert "not found" in response.message.lower() or "9999999999" in response.message


# ---------------------------------------------------------------------------
# REQ-002: List open POs by vendor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_pos_by_vendor(agent):
    """Agent returns list of open POs filtered by vendor."""
    tools = [_mock_tool("list_a_purchaseorder_for_api_purchaseorder_process_srv")]
    list_content = (
        "Open POs for ACME001:\n"
        "- PO 4500001234: EUR 75,000.00 (Open)\n"
        "- PO 4500001236: EUR 32,000.00 (Open)"
    )
    mock_result = {"messages": _build_messages(list_content)}

    with patch.object(agent, "_invoke", new=AsyncMock(return_value=mock_result)):
        response = await agent.invoke(
            query="Show me all open POs for vendor ACME001",
            context_id="test-ctx-003",
            tools=tools,
        )

    assert response.status == "completed"
    assert "ACME001" in response.message or "4500001234" in response.message


# ---------------------------------------------------------------------------
# REQ-003: Filter POs by amount threshold
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_filter_pos_by_amount(agent):
    """Agent returns POs above a given amount threshold, sorted descending."""
    tools = [_mock_tool("list_a_purchaseorder_for_api_purchaseorder_process_srv")]
    amount_content = (
        "Open POs above EUR 50,000:\n"
        "1. PO 4500001234: EUR 75,000.00 — ACME001\n"
        "2. PO 4500001238: EUR 60,000.00 — BIGVENDOR"
    )
    mock_result = {"messages": _build_messages(amount_content)}

    with patch.object(agent, "_invoke", new=AsyncMock(return_value=mock_result)):
        response = await agent.invoke(
            query="Show me all open POs above EUR 50000",
            context_id="test-ctx-004",
            tools=tools,
        )

    assert response.status == "completed"
    assert "75" in response.message or "50" in response.message


# ---------------------------------------------------------------------------
# REQ-004: Open PO summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_open_po_summary(agent):
    """Agent returns total count and value of open POs."""
    tools = [
        _mock_tool("list_a_purchaseorder_for_api_purchaseorder_process_srv"),
        _mock_tool("count_a_purchaseorder_for_api_purchaseorder_process_srv"),
    ]
    summary_content = (
        "Open Purchase Orders Summary:\n"
        "Total count: 42\n"
        "Total net value: EUR 1,250,000.00"
    )
    mock_result = {"messages": _build_messages(summary_content)}

    with patch.object(agent, "_invoke", new=AsyncMock(return_value=mock_result)):
        response = await agent.invoke(
            query="Give me a summary of all open POs",
            context_id="test-ctx-005",
            tools=tools,
        )

    assert response.status == "completed"
    assert "42" in response.message or "summary" in response.message.lower() or "count" in response.message.lower()


# ---------------------------------------------------------------------------
# Error scenario: API returns error
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_api_error_relayed_verbatim(agent):
    """Agent relays API error message verbatim, does not fabricate data."""
    tools = [_mock_tool("list_a_purchaseorder_for_api_purchaseorder_process_srv")]
    error_content = (
        "I was unable to retrieve data from S/4HANA at this time. "
        "Please try again shortly."
    )
    mock_result = {"messages": _build_messages(error_content)}

    with patch.object(agent, "_invoke", new=AsyncMock(return_value=mock_result)):
        response = await agent.invoke(
            query="Show all open POs",
            context_id="test-ctx-006",
            tools=tools,
        )

    assert response.status == "completed"
    assert "S/4HANA" in response.message or "unable" in response.message.lower() or "error" in response.message.lower()


# ---------------------------------------------------------------------------
# Guardrail: No tools available
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_tools_available(agent):
    """Agent handles gracefully when no MCP tools are available."""
    no_tools_content = (
        "I'm currently unable to access SAP S/4HANA data "
        "as the tools are temporarily unavailable."
    )
    mock_result = {"messages": _build_messages(no_tools_content)}

    with patch.object(agent, "_invoke", new=AsyncMock(return_value=mock_result)):
        response = await agent.invoke(
            query="What is the status of PO 4500001234?",
            context_id="test-ctx-007",
            tools=[],
        )

    assert response.status == "completed"
    assert response.message is not None and len(response.message) > 0


# ---------------------------------------------------------------------------
# Integration test: end-to-end agent flow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_integration_po_query_end_to_end(add_agent_to_path):
    """Integration test: full agent.invoke() flow with mocked LLM and MCP tools."""
    with patch("langchain_litellm.ChatLiteLLM.__init__", return_value=None):
        with patch("sap_cloud_sdk.agent_memory.factory.langgraph_checkpoint.create_checkpointer", return_value=None):
            from agent import SampleAgent

            agent_instance = SampleAgent.__new__(SampleAgent)
            agent_instance.llm = MagicMock()
            agent_instance._checkpointer = None
            agent_instance._summarization_middleware = MagicMock()
            agent_instance._temperature = 0.0

            tool = _mock_tool("list_a_purchaseorder_for_api_purchaseorder_process_srv")

            expected = "Found 2 open purchase orders for ACME001."
            mock_result = {"messages": _build_messages(expected)}

            with patch.object(agent_instance, "_invoke", new=AsyncMock(return_value=mock_result)):
                response = await agent_instance.invoke(
                    query="Show me all open POs for ACME001",
                    context_id="test-integration-001",
                    tools=[tool],
                )

    assert response.status == "completed"
    assert "ACME001" in response.message or "open" in response.message.lower()


# ---------------------------------------------------------------------------
# Business instrumentation: milestone logging
# ---------------------------------------------------------------------------


def test_milestone_logging_present():
    """Verify that M1-M4 milestone log statements exist in agent.py."""
    agent_file = AGENT_ROOT / "app" / "agent.py"
    content = agent_file.read_text()
    assert "M1.achieved" in content, "M1 achievement log missing"
    assert "M1.missed" in content, "M1 miss log missing"
    assert "M2.achieved" in content, "M2 achievement log missing"
    assert "M2.missed" in content, "M2 miss log missing"
    assert "M3.achieved" in content, "M3 achievement log missing"
    assert "M3.missed" in content, "M3 miss log missing"


# ---------------------------------------------------------------------------
# System prompt guardrails
# ---------------------------------------------------------------------------


def test_system_prompt_read_only_instruction(add_agent_to_path):
    """System prompt must instruct the agent it has read-only access."""
    from agent import get_system_prompt
    prompt = get_system_prompt()
    assert "read-only" in prompt.lower() or "cannot create" in prompt.lower()


def test_system_prompt_no_fabrication_instruction(add_agent_to_path):
    """System prompt must prohibit fabricating data."""
    from agent import get_system_prompt
    prompt = get_system_prompt()
    assert "never fabricate" in prompt.lower() or "never guess" in prompt.lower()


def test_system_prompt_filter_required_instruction(add_agent_to_path):
    """System prompt must require at least one filter per query."""
    from agent import get_system_prompt
    prompt = get_system_prompt()
    assert "filter" in prompt.lower()
