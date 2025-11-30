"""
Tests for NeuroCopilot endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_copilot_chat(client: AsyncClient, auth_headers):
    """Test chatting with NeuroCopilot."""
    response = await client.post(
        "/api/v1/copilot/chat",
        headers=auth_headers,
        json={
            "content": "Hello, what can you help me with?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert len(data["message"]) > 0


@pytest.mark.asyncio
async def test_copilot_suggestions(client: AsyncClient, auth_headers):
    """Test getting copilot suggestions."""
    response = await client.get(
        "/api/v1/copilot/suggestions",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0


@pytest.mark.asyncio
async def test_copilot_capabilities(client: AsyncClient, auth_headers):
    """Test getting copilot capabilities."""
    response = await client.get(
        "/api/v1/copilot/capabilities",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "capabilities" in data
    assert len(data["capabilities"]) > 0


@pytest.mark.asyncio
async def test_copilot_create_campaign_intent(client: AsyncClient, auth_headers):
    """Test copilot understands campaign creation intent."""
    response = await client.post(
        "/api/v1/copilot/chat",
        headers=auth_headers,
        json={
            "content": "Create a new marketing campaign for Black Friday",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    # Response should mention campaign creation
    assert any(word in data["message"].lower() for word in ["campaign", "create", "black friday"])


@pytest.mark.asyncio
async def test_copilot_analyze_intent(client: AsyncClient, auth_headers):
    """Test copilot understands analysis intent."""
    response = await client.post(
        "/api/v1/copilot/chat",
        headers=auth_headers,
        json={
            "content": "Analyze my marketing performance this month",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert any(word in data["message"].lower() for word in ["analyze", "performance", "metrics"])

