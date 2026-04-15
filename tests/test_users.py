def test_register_user(client):
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "Secret123!"
    }

    response = client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["name"] == payload["name"]
    assert "id" in data


def test_duplicate_email_registration(client):
    payload = {
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "Secret123!"
    }

    response = client.post("/register", json=payload)
    assert response.status_code == 201

    duplicate_response = client.post("/register", json=payload)
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Email already registered"


def test_register_name_too_long(client):
    payload = {
        "name": "A" * 21,
        "email": "longname@example.com",
        "password": "Secret123!"
    }

    response = client.post("/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Name must be at most 20 characters long"


def test_register_password_too_short(client):
    payload = {
        "name": "Short Password",
        "email": "shortpass@example.com",
        "password": "1234567"
    }

    response = client.post("/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Password must be at least 8 characters long"


def test_login_success(client):
    register_payload = {
        "name": "Login User",
        "email": "login@example.com",
        "password": "Secret123!"
    }
    client.post("/register", json=register_payload)

    login_payload = {"email": register_payload["email"], "password": register_payload["password"]}
    login_response = client.post("/login", json=login_payload)

    assert login_response.status_code == 200
    data = login_response.json()
    assert data["message"] == "Login successful"
    assert "user_id" in data
    assert "token" in data
    assert data["token"]["token_type"] == "bearer"
    assert data["token"]["access_token"]


def test_login_wrong_password(client):
    register_payload = {
        "name": "Wrong Password User",
        "email": "wrongpass@example.com",
        "password": "Secret123!"
    }
    client.post("/register", json=register_payload)

    login_payload = {"email": register_payload["email"], "password": "WrongPassword"}
    response = client.post("/login", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_me_requires_auth(client):
    response = client.get("/me")
    assert response.status_code == 401


def test_get_me_success(client):
    register_payload = {
        "name": "Me User",
        "email": "me@example.com",
        "password": "Secret123!"
    }
    client.post("/register", json=register_payload)

    login_response = client.post(
        "/login",
        json={"email": register_payload["email"], "password": register_payload["password"]}
    )
    token = login_response.json()["token"]["access_token"]

    me_response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == register_payload["email"]
