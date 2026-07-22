import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "dr_smith", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_failure(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "dr_smith", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    import uuid
    username = f"testuser_{uuid.uuid4()}"
    
    # Register
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "securepassword", "role": "customer"}
    )
    assert response.status_code == 200
    
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_forgot_and_reset_password(client: AsyncClient):
    import uuid
    username = f"testuser_{uuid.uuid4()}"
    
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "oldpassword", "role": "customer"}
    )
    
    # Forgot password
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"username": username}
    )
    assert response.status_code == 200
    data = response.json()
    token = data["reset_token"]
    
    # Reset password
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "newpassword"}
    )
    assert response.status_code == 200
    
    # Login with new password
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "newpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
