def test_create_article(client):
    payload = {
        "title": "AI News Update",
        "content": "Artificial intelligence is transforming news research.",
        "source_url": "https://example.com/news"
    }

    response = client.post("/articles", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["source_url"] == payload["source_url"]
    assert "id" in data


def test_get_all_articles(client):
    first_article = {
        "title": "First AI Story",
        "content": "The first test article.",
        "source_url": "https://example.com/first"
    }
    second_article = {
        "title": "Second AI Story",
        "content": "The second test article.",
        "source_url": "https://example.com/second"
    }

    client.post("/articles", json=first_article)
    client.post("/articles", json=second_article)

    response = client.get("/articles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_single_article(client):
    payload = {
        "title": "Single Article",
        "content": "The content for a single article test.",
        "source_url": "https://example.com/single"
    }

    create_response = client.post("/articles", json=payload)
    article_id = create_response.json()["id"]

    get_response = client.get(f"/articles/{article_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == article_id


def test_delete_article(client):
    payload = {
        "title": "Delete Article",
        "content": "This article will be deleted.",
        "source_url": "https://example.com/delete"
    }

    create_response = client.post("/articles", json=payload)
    article_id = create_response.json()["id"]

    delete_response = client.delete(f"/articles/{article_id}")
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

    article_payload = {
        "title": "Saved Article",
        "content": "A saved article example.",
        "source_url": "https://example.com/saved"
    }
    article_response = client.post("/articles", json=article_payload)
    article_id = article_response.json()["id"]

    save_payload = {"user_id": user_id, "article_id": article_id}
    save_response = client.post("/save", json=save_payload)
    assert save_response.status_code == 201
    save_data = save_response.json()
    assert save_data["user_id"] == user_id
    assert save_data["article_id"] == article_id

    saved_list_response = client.get(f"/saved/{user_id}")
    assert saved_list_response.status_code == 200
    saved_items = saved_list_response.json()
    assert isinstance(saved_items, list)
    assert len(saved_items) == 1
    assert saved_items[0]["article_id"] == article_id
