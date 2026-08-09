from pathlib import Path

import pytest

from wick import models


def test_resolve_prefers_an_explicit_path():
    explicit = Path("somewhere/custom.gguf")
    assert models.resolve(explicit) == explicit


def test_resolve_finds_a_model_in_a_search_directory(monkeypatch, tmp_path):
    downloaded = tmp_path / models.CATALOG[models.DEFAULT_MODEL].filename
    downloaded.touch()
    monkeypatch.setattr(models, "SEARCH_DIRS", (tmp_path,))

    assert models.resolve(None) == downloaded


def test_resolve_points_at_the_download_command_when_nothing_is_local(monkeypatch, tmp_path):
    monkeypatch.setattr(models, "SEARCH_DIRS", (tmp_path,))

    with pytest.raises(FileNotFoundError, match="--download-model"):
        models.resolve(None)


def test_unknown_model_name_is_rejected():
    with pytest.raises(ValueError, match="Unknown model"):
        models.resolve(None, "not-a-real-model")
