"""
Tests for campaign endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.fixture
async def test_organization(db_session, test_user):
    """Create test organization."""
    from app.models.organization import Organization, OrganizationMember
    
    org = Organization(
        name="Test Company",
        slug="test-company",
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    
    # Add user as owner
    member = OrganizationMember(
        organization_id=org.id,
        user_id=test_user.id,
        role="owner",
    )
    db_session.add(member)
    await db_session.commit()
    
    return org


@pytest.fixture
async def test_campaign(db_session, test_organization):
    """Create test campaign."""
    from app.models.campaign import Campaign
    
    campaign = Campaign(
        organization_id=test_organization.id,
        name="Test Campaign",
        status="draft",
        campaign_type="awareness",
    )
    db_session.add(campaign)
    await db_session.commit()
    await db_session.refresh(campaign)
    return campaign


@pytest.mark.asyncio
async def test_list_campaigns(
    client: AsyncClient,
    auth_headers,
    test_organization,
    test_campaign,
):
    """Test listing campaigns."""
    response = await client.get(
        f"/api/v1/campaigns/?org_id={test_organization.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "campaigns" in data
    assert len(data["campaigns"]) >= 1


@pytest.mark.asyncio
async def test_create_campaign(
    client: AsyncClient,
    auth_headers,
    test_organization,
):
    """Test creating a campaign."""
    response = await client.post(
        f"/api/v1/campaigns/?org_id={test_organization.id}",
        headers=auth_headers,
        json={
            "name": "New Campaign",
            "campaign_type": "conversion",
            "channels": ["google", "meta"],
            "budget": 1000.0,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Campaign"
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_get_campaign(
    client: AsyncClient,
    auth_headers,
    test_organization,
    test_campaign,
):
    """Test getting a specific campaign."""
    response = await client.get(
        f"/api/v1/campaigns/{test_campaign.id}?org_id={test_organization.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Campaign"


@pytest.mark.asyncio
async def test_update_campaign(
    client: AsyncClient,
    auth_headers,
    test_organization,
    test_campaign,
):
    """Test updating a campaign."""
    response = await client.put(
        f"/api/v1/campaigns/{test_campaign.id}?org_id={test_organization.id}",
        headers=auth_headers,
        json={
            "name": "Updated Campaign",
            "status": "active",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Campaign"


@pytest.mark.asyncio
async def test_delete_campaign(
    client: AsyncClient,
    auth_headers,
    test_organization,
    test_campaign,
):
    """Test deleting a campaign."""
    response = await client.delete(
        f"/api/v1/campaigns/{test_campaign.id}?org_id={test_organization.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_campaign_unauthorized_org(
    client: AsyncClient,
    auth_headers,
):
    """Test accessing campaign from unauthorized org."""
    fake_org_id = str(uuid4())
    response = await client.get(
        f"/api/v1/campaigns/?org_id={fake_org_id}",
        headers=auth_headers,
    )
    assert response.status_code == 403

