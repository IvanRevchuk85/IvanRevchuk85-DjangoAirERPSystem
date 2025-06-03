import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_check_success(admin_client: AsyncClient):
    # Sending a GET request to the admin endpoint
    response = await admin_client.get("/admin/check")

    # Checking that the status is 200 (OK)
    assert response.status_code == 200

    message = response.json().get("message")

    # Checking that the response contains an email and the word "admin"
    assert "admin@test.com" in message
    assert "admin" in message.lower()
    assert message == "Welcome, admin admin@test.com!"
