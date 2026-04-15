def _auth_headers(client, email="articleuser@example.com"):
    register_payload = {
        "name": "Article User",
        "email": email,
        "password": "Secret123!"
    }
    client.post("/register", json=register_payload)
    login_response = client.post("/login", json={"email": email, "password": "Secret123!"})
    token = login_response.json()["token"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_article(client):
    headers = _auth_headers(client)
    payload = {
        "title": "AI News Update",
        "content": "Artificial intelligence is transforming news research.",
        "category": "Technology",
        "source_url": "https://example.com/news"
    }

    response = client.post("/articles", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["category"] == payload["category"]
    assert data["source_url"] == payload["source_url"]
    assert "id" in data


def test_get_all_articles(client):
    headers = _auth_headers(client)
    first_article = {
        "title": "First AI Story",
        "content": "The first test article.",
        "category": "Technology",
        "source_url": "https://example.com/first"
    }
    second_article = {
        "title": "Second AI Story",
        "content": "The second test article.",
        "category": "Sports",
        "source_url": "https://example.com/second"
    }

    client.post("/articles", json=first_article, headers=headers)
    client.post("/articles", json=second_article, headers=headers)

    response = client.get("/articles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    filtered = client.get("/articles", params={"category": "Sports"})
    assert filtered.status_code == 200
    filtered_data = filtered.json()
    assert len(filtered_data) == 1
    assert filtered_data[0]["category"] == "Sports"


def test_get_single_article(client):
    headers = _auth_headers(client)
    payload = {
        "title": "Single Article",
        "content": "The content for a single article test.",
        "category": "Economy",
        "source_url": "https://example.com/single"
    }

    create_response = client.post("/articles", json=payload, headers=headers)
    article_id = create_response.json()["id"]

    get_response = client.get(f"/articles/{article_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == article_id


def test_delete_article(client):
    headers = _auth_headers(client)
    payload = {
        "title": "Delete Article",
        "content": "This article will be deleted.",
        "category": "Politics",
        "source_url": "https://example.com/delete"
    }

    create_response = client.post("/articles", json=payload, headers=headers)
    article_id = create_response.json()["id"]

    delete_response = client.delete(f"/articles/{article_id}", headers=headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/articles/{article_id}")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Article not found"


def test_save_article_and_get_saved_articles(client):
    user_payload = {
        "name": "Save User",
        "email": "saveuser@example.com",
        "password": "Secret123!"
    }
    register_response = client.post("/register", json=user_payload)
    user_id = register_response.json()["id"]

    login_response = client.post("/login", json={"email": user_payload["email"], "password": user_payload["password"]})
    token = login_response.json()["token"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    article_payload = {
        "title": "Saved Article",
        "content": "A saved article example.",
        "category": "Technology",
        "source_url": "https://example.com/saved"
    }
    article_response = client.post("/articles", json=article_payload, headers=headers)
    article_id = article_response.json()["id"]

    save_payload = {"user_id": user_id, "article_id": article_id}
    save_response = client.post("/save", json=save_payload, headers=headers)
    assert save_response.status_code == 201
    save_data = save_response.json()
    assert save_data["user_id"] == user_id
    assert save_data["article_id"] == article_id

    saved_list_response = client.get(f"/saved/{user_id}", headers=headers)
    assert saved_list_response.status_code == 200
    saved_items = saved_list_response.json()
    assert isinstance(saved_items, list)
    assert len(saved_items) == 1
    assert saved_items[0]["article_id"] == article_id


def test_get_single_article_hydrates_truncated_content(client, monkeypatch):
    headers = _auth_headers(client, email="hydrate@example.com")
    payload = {
        "title": "Hydration Test Article",
        "content": "Short teaser from API source... [+3924 chars]",
        "category": "Technology",
        "source_url": "https://example.com/full-story"
    }

    create_response = client.post("/articles", json=payload, headers=headers)
    article_id = create_response.json()["id"]

    article_service = __import__("app.services.article_content_service", fromlist=["fetch_full_article_text"])

    full_text = (
        "This is the first full paragraph with context and detail. " * 10
        + "\n\n"
        + "This is the second paragraph that extends the complete article body. " * 10
    )

    monkeypatch.setattr(article_service, "fetch_full_article_text", lambda url: full_text)

    get_response = client.get(f"/articles/{article_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["content"] == full_text
    assert "[+3924 chars]" not in data["content"]


def test_get_single_article_hydrates_short_teaser_content(client, monkeypatch):
    headers = _auth_headers(client, email="shortteaser@example.com")
    payload = {
        "title": "Short Teaser Article",
        "content": "A short teaser sentence from the publisher homepage.",
        "category": "Technology",
        "source_url": "https://example.com/teaser-story"
    }

    create_response = client.post("/articles", json=payload, headers=headers)
    article_id = create_response.json()["id"]

    article_service = __import__("app.services.article_content_service", fromlist=["fetch_full_article_text"])

    full_text = (
        "This is a much longer article body with enough detail to be considered a real article for summary generation. " * 14
    )

    monkeypatch.setattr(article_service, "fetch_full_article_text", lambda url: full_text)

    get_response = client.get(f"/articles/{article_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["content"] == full_text
    assert len(data["content"].split()) >= 120
