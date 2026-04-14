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
    assert login_response.json()["message"] == "Login successful"
    assert "user_id" in login_response.json()


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
