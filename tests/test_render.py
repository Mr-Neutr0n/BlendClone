from pathlib import Path

import pytest

from app import render

BLENDER_ROOT = Path("C:/Program Files/Blender Foundation")
MAC_APP = Path("/Applications/Blender.app/Contents/MacOS/Blender")
OPT_ROOT = Path("/opt")


def fake_glob(roots):
    """Return a glob that answers from {path: {pattern: candidates}}."""

    def glob(self, pattern):
        return roots.get(self, {}).get(pattern, [])

    return glob


def test_blender_binary_picks_newest_by_version(monkeypatch):
    monkeypatch.delenv("BLENDER_PATH", raising=False)
    monkeypatch.setattr(render.shutil, "which", lambda name: None)
    candidates = [
        Path("C:/Program Files/Blender Foundation/Blender 5.9/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 5.10/blender.exe"),
    ]
    monkeypatch.setattr(
        render.Path,
        "glob",
        fake_glob({BLENDER_ROOT: {"Blender */blender.exe": candidates}}),
    )
    assert render.blender_binary() == str(candidates[1])


def test_blender_binary_skips_versions_below_5_1(monkeypatch):
    monkeypatch.delenv("BLENDER_PATH", raising=False)
    monkeypatch.setattr(render.shutil, "which", lambda name: None)
    candidates = [
        Path("C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"),
    ]
    monkeypatch.setattr(
        render.Path,
        "glob",
        fake_glob({BLENDER_ROOT: {"Blender */blender.exe": candidates}}),
    )
    with pytest.raises(ValueError, match="Blender is missing"):
        render.blender_binary()


def test_blender_binary_keeps_unversioned_mac_app(monkeypatch):
    monkeypatch.delenv("BLENDER_PATH", raising=False)
    monkeypatch.setattr(render.shutil, "which", lambda name: None)
    monkeypatch.setattr(
        render.Path,
        "glob",
        fake_glob({Path("/Applications"): {"Blender*.app/Contents/MacOS/Blender": [MAC_APP]}}),
    )
    assert render.blender_binary() == str(MAC_APP)


def test_blender_binary_keeps_unversioned_linux_tarball(monkeypatch):
    monkeypatch.delenv("BLENDER_PATH", raising=False)
    monkeypatch.setattr(render.shutil, "which", lambda name: None)
    binary = Path("/opt/blender/blender")
    monkeypatch.setattr(
        render.Path,
        "glob",
        fake_glob({OPT_ROOT: {"blender*/blender": [binary]}}),
    )
    assert render.blender_binary() == str(binary)


def test_blender_binary_prefers_versioned_over_unversioned(monkeypatch):
    monkeypatch.delenv("BLENDER_PATH", raising=False)
    monkeypatch.setattr(render.shutil, "which", lambda name: None)
    versioned = Path("/opt/blender-5.1/blender")
    monkeypatch.setattr(
        render.Path,
        "glob",
        fake_glob(
            {
                Path("/Applications"): {"Blender*.app/Contents/MacOS/Blender": [MAC_APP]},
                OPT_ROOT: {"blender*/blender": [Path("/opt/blender/blender"), versioned]},
            }
        ),
    )
    assert render.blender_binary() == str(versioned)
