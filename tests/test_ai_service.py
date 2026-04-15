from app.services.ai_service import summarize_text


def test_fallback_key_points_are_clean_and_not_mid_word_cut():
    text = (
        "Government officials from multiple departments announced a comprehensive urban mobility initiative "
        "to reduce congestion and improve public transit reliability across central and suburban districts. "
        "The plan introduces phased bus-lane expansion, revised train timetables, and infrastructure upgrades "
        "scheduled over the next twelve months, with public consultations planned in each municipality. "
        "Analysts and resident groups are evaluating expected economic impacts, commute-time reductions, "
        "and long-term sustainability outcomes tied to the project."
    )

    result = summarize_text(text)

    assert isinstance(result, dict)
    assert "summary" in result
    assert "key_points" in result
    assert isinstance(result["key_points"], list)
    assert len(result["key_points"]) >= 1

    for point in result["key_points"]:
        assert isinstance(point, str)
        assert point.strip() == point
        # 120 chars + optional ellipsis when truncated
        assert len(point) <= 123
