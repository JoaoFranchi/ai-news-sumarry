import importlib


def test_summarize_endpoint_returns_summary(client, monkeypatch):
    ai_module = importlib.import_module("app.routes.ai")

    def mock_summarize_text(text):
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
        "text": "AI research continues to improve and deliver faster models for real-world usage.",
        "article_id": None
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

    def mock_summarize_text(text):
        return {
            "summary": "AI testing summary stored successfully.",
            "key_points": ["Stored summary point"]
        }

    monkeypatch.setattr(ai_module, "summarize_text", mock_summarize_text)

    payload = {
        "text": "A final news article used for testing storage.",
        "article_id": None
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

    def mock_summarize_text(text):
        return {
            "summary": "A list test summary.",
            "key_points": ["List point"]
        }

    monkeypatch.setattr(ai_module, "summarize_text", mock_summarize_text)
    client.post("/summarize", json={"text": "Some news text", "article_id": None})

    response = client.get("/summaries")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert any(item["summary_text"] == "A list test summary." for item in items)
