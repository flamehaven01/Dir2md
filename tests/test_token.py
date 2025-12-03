from dir2md.token import estimate_tokens


def test_estimate_tokens_basics():
    assert estimate_tokens("") == 1
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("abcdefgh") == 2  # 8 chars -> 2 tokens with ceil
    assert estimate_tokens("a" * 9) == 3  # round up
