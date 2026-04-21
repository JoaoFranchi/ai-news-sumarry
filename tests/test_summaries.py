import importlib


def test_summarize_endpoint_returns_summary(client, monkeypatch):
    ai_module = importlib.import_module("app.routes.ai")

    def mock_summarize_text(text, length):
        return {
            "summary": "This article explains the news in three concise sentences.",
            "key_points": [
                "First key point",
                "Second key point",
                "Third key point"
            ]
        }

    monkeypatch.setattr(ai_module, "summarize_text", mock_summarize_text)

    payload = {
        "article_text": "AI research continues to improve and deliver faster models for real-world usage.",
        "article_id": None,
        "length": "medium",
    }
    response = client.post("/summarize", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "This article explains the news in three concise sentences."
    assert isinstance(data["key_points"], list)
    assert len(data["key_points"]) == 3
    assert "summary_id" in data


def test_summary_is_stored_in_database(client, monkeypatch):
    ai_module = importlib.import_module("app.routes.ai")

    def mock_summarize_text(text, length):
        return {
            "summary": "AI testing summary stored successfully.",
            "key_points": ["Stored summary point"]
        }

    monkeypatch.setattr(ai_module, "summarize_text", mock_summarize_text)

    payload = {
        "article_text": "A final news article used for testing storage.",
        "article_id": None,
        "length": "short",
    }
    create_response = client.post("/summarize", json=payload)
    summary_id = create_response.json()["summary_id"]

    stored_response = client.get(f"/summaries/{summary_id}")
    assert stored_response.status_code == 200
    stored_data = stored_response.json()
    assert stored_data["summary_text"] == "AI testing summary stored successfully."
    assert stored_data["id"] == summary_id


def test_list_summaries_returns_stored_summary(client, monkeypatch):
    ai_module = importlib.import_module("app.routes.ai")

    def mock_summarize_text(text, length):
        return {
            "summary": "A list test summary.",
            "key_points": ["List point"]
        }

    monkeypatch.setattr(ai_module, "summarize_text", mock_summarize_text)
    client.post("/summarize", json={"article_text": "Some news text", "article_id": None, "length": "long"})

    response = client.get("/summaries")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert any(item["summary_text"] == "A list test summary." for item in items)


def test_summarize_short_article_returns_informative_message(client):
    payload = {
        "article_text": "AI wins.",
        "article_id": None,
        "length": "medium",
    }
    response = client.post("/summarize", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Article too short to summarize effectively"
    assert data["key_points"] == []
    assert "summary_id" in data


def test_summarize_rejects_invalid_length(client):
    payload = {
        "article_text": "This is a valid article text with enough words to pass minimal checks for summarization behavior in tests.",
        "article_id": None,
        "length": "extra-long",
    }

    response = client.post("/summarize", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "length must be one of: short, medium, long"
