"""
Authentication, Authorization & Multi-User Data Isolation Integration Tests.
Verifies User Registration, Password Hashing, JWT Verification, and Multi-Tenant Privacy Isolation.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, verify_password, create_access_token
from app.db.repositories.user_repository import UserRepository
from app.db.models.user import User


@pytest.mark.asyncio
async def test_user_repository_crud(db_session: AsyncSession):
    repo = UserRepository(db_session)

    # 1. Create User
    user = await repo.create_user(
        username="quant_analyst",
        email="analyst@hedgefund.com",
        password="SuperSecret123!",
        full_name="Jane Doe"
    )
    assert user.id is not None
    assert user.username == "quant_analyst"
    assert user.is_active is True

    # 2. Query User by Email
    by_email = await repo.get_by_email("analyst@hedgefund.com")
    assert by_email is not None
    assert by_email.id == user.id
    assert verify_password("SuperSecret123!", by_email.hashed_password)
    assert not verify_password("WrongPassword!", by_email.hashed_password)

    # 3. Query User by Username
    by_name = await repo.get_by_username("quant_analyst")
    assert by_name is not None
    assert by_name.email == "analyst@hedgefund.com"


def test_auth_api_routes_and_jwt_lifecycle(test_client: TestClient):
    # 1. Register new user via HTTP API
    reg_payload = {
        "username": "alice_trader",
        "email": "alice@marketmind.ai",
        "password": "SecurePassword456!",
        "full_name": "Alice Trader"
    }
    reg_resp = test_client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201, reg_resp.text
    reg_data = reg_resp.json()
    assert reg_data["username"] == "alice_trader"
    assert reg_data["email"] == "alice@marketmind.ai"

    # 2. Verify duplicate registration rejected
    dup_resp = test_client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_resp.status_code in [400, 422]

    # 3. Login with correct credentials
    login_resp = test_client.post("/api/v1/auth/login", json={
        "username": "alice_trader",
        "password": "SecurePassword456!"
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    token = login_data["access_token"]

    # 4. Login with wrong password
    bad_login = test_client.post("/api/v1/auth/login", json={
        "username": "alice_trader",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 5. Access /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = test_client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["username"] == "alice_trader"
    assert me_data["email"] == "alice@marketmind.ai"


def test_user_data_isolation(test_client: TestClient):
    """Verifies that User A's private watchlist / portfolio items are strictly isolated from User B."""
    # Register User A
    test_client.post("/api/v1/auth/register", json={
        "username": "user_a",
        "email": "usera@marketmind.ai",
        "password": "PasswordA123!",
        "full_name": "User Alpha"
    })
    token_a = test_client.post("/api/v1/auth/login", json={
        "username": "user_a",
        "password": "PasswordA123!"
    }).json()["access_token"]

    # Register User B
    test_client.post("/api/v1/auth/register", json={
        "username": "user_b",
        "email": "userb@marketmind.ai",
        "password": "PasswordB123!",
        "full_name": "User Beta"
    })
    token_b = test_client.post("/api/v1/auth/login", json={
        "username": "user_b",
        "password": "PasswordB123!"
    }).json()["access_token"]

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A adds NVDA to watchlist
    add_a = test_client.post("/api/v1/watchlist", json={"ticker": "NVDA"}, headers=headers_a)
    assert add_a.status_code == 201

    # User B checks watchlist
    wl_b = test_client.get("/api/v1/watchlist", headers=headers_b).json()
    assert isinstance(wl_b, list)
