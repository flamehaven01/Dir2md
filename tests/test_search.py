from dir2md.search import match_query_snippet


def test_match_query_snippet_hits():
    text = "hello quantum engine world"
    score, snippet = match_query_snippet(text, "quantum")
    assert score >= 1
    assert "quantum" in snippet.lower()


def test_match_query_snippet_miss():
    text = "hello world"
    score, snippet = match_query_snippet(text, "missing")
    assert score == 0
    assert snippet == ""
