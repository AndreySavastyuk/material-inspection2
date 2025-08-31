"""
Тесты аутентификации
"""
import pytest
from httpx import AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_login_with_valid_credentials():
    """Тест входа с валидными данными"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Используем тестового пользователя
        response = await client.post("/api/v1/auth/login", json={
            "email": "admin@example.com",
            "password": "password"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "admin@example.com"
        assert data["user"]["role"] == "administrator"


@pytest.mark.asyncio
async def test_login_with_invalid_credentials():
    """Тест входа с неверными данными"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", json={
            "email": "admin@example.com",
            "password": "wrong_password"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_login_with_nonexistent_user():
    """Тест входа с несуществующим пользователем"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_register_new_user():
    """Тест регистрации нового пользователя"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User",
            "role": "warehouse_keeper"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["role"] == "warehouse_keeper"
        assert data["is_active"] is True
        assert "id" in data


@pytest.mark.asyncio
async def test_register_existing_user():
    """Тест регистрации существующего пользователя"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json={
            "email": "admin@example.com",
            "password": "password123",
            "full_name": "Admin User",
            "role": "administrator"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_with_invalid_role():
    """Тест регистрации с неверной ролью"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json={
            "email": "invalidrole@example.com",
            "password": "password123",
            "full_name": "Invalid Role User",
            "role": "invalid_role"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid role" in data["detail"]


@pytest.mark.asyncio
async def test_get_current_user():
    """Тест получения информации о текущем пользователе"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Сначала логинимся
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "admin@example.com",
            "password": "password"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Получаем информацию о пользователе
        response = await client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "admin@example.com"
        assert data["role"] == "administrator"
        assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_current_user_without_token():
    """Тест получения информации о пользователе без токена"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token():
    """Тест получения информации о пользователе с неверным токеном"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid_token"
        })
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token():
    """Тест обновления токена"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Сначала логинимся
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "admin@example.com",
            "password": "password"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Обновляем токен
        response = await client.post("/api/v1/auth/refresh", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_logout():
    """Тест выхода из системы"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Сначала логинимся
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "admin@example.com",
            "password": "password"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Выходим из системы
        response = await client.post("/api/v1/auth/logout", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"


@pytest.mark.asyncio
async def test_multiple_user_roles():
    """Тест различных ролей пользователей"""
    test_roles = [
        ("warehouse@example.com", "warehouse_keeper"),
        ("qc@example.com", "quality_control"),
        ("lab_destructive@example.com", "lab_destructive"),
        ("lab_non_destructive@example.com", "lab_non_destructive"),
        ("production@example.com", "production")
    ]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        for email, expected_role in test_roles:
            response = await client.post("/api/v1/auth/login", json={
                "email": email,
                "password": "password"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["user"]["role"] == expected_role
            assert data["user"]["email"] == email