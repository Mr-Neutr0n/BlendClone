from pathlib import Path

import pytest

from app import render


def test_blender_binary_picks_newest_by_version(monkeypatch):
    monkeypatch.delenv("BLENDER_PATH", raising=False)
    monkeypatch.setattr(render.shutil, "which", lambda name: None)
    candidates = [
        Path("C:/Program Files/Blender Foundation/Blender 5.9/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 5.10/blender.exe"),
    ]

    def fake_glob(self, pattern):
        if str(self) == "C:/Program Files/Blender Foundation" and pattern == "Blender */blender.exe":
            return candidates
        return []

    monkeypatch.setattr(render.Path, "glob", fake_glob)
    assert render.blender_binary() == str(candidates[1])


def test_blender_binary_skips_versions_below_5_1(monkeypatch):
    monkeypatch.delenv("BLENDER_PATH", raising=False)
    monkeypatch.setattr(render.shutil, "which", lambda name: None)
    candidates = [
        Path("C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"),
    ]

    def fake_glob(self, pattern):
        if str(self) == "C:/Program Files/Blender Foundation" and pattern == "Blender */blender.exe":
            return candidates
        return []

    monkeypatch.setattr(render.Path, "glob", fake_glob)
    with pytest.raises(ValueError, match="Blender is missing"):
        render.blender_binary()
