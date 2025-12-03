from dir2md.cli import DEFAULT_EXCLUDES


def test_default_excludes_cover_venv_noise():
    noise = {".venv", "venv", "venv_clean", ".pytest_cache"}
    assert noise.issubset(set(DEFAULT_EXCLUDES))
