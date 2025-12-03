from dir2md.masking import apply_masking


def test_masking_basic_masks_aws_key():
    text = "key=AKIAIOSFODNN7EXAMPLE"
    masked = apply_masking(text, mode="basic")
    assert "AKIAIOSFODNN7EXAMPLE" not in masked
    assert "[*** MASKED_SECRET ***]" in masked


def test_masking_off_keeps_content():
    text = "secret=abc123"
    masked = apply_masking(text, mode="off")
    assert "abc123" in masked
