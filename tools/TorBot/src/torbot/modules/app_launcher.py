"""
Optional TorBot desktop app launcher.

The Electron UI lives outside the Python package so CLI users do not need Node
or Electron dependencies. This module only discovers and starts that sibling
project when the user explicitly requests it.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


TORBOT_APP_REPOSITORY_URL = "https://github.com/KingAkeem/TorBotApp"


def _looks_like_torbot_app(path: Path) -> bool:
    return path.is_dir() and (path / "package.json").is_file()


def find_torbot_app(
    repo_root: str | os.PathLike[str],
    app_dir: str | None = None,
) -> Path | None:
    """
    Find an optional TorBotApp checkout.

    Discovery order:
    1. Explicit --app-dir value.
    2. TORBOT_APP_DIR environment variable.
    3. Sibling TorBotApp directory next to this repository.
    """
    if app_dir:
        resolved = Path(app_dir).expanduser().resolve()
        return resolved if _looks_like_torbot_app(resolved) else None

    candidates = []
    env_app_dir = os.environ.get("TORBOT_APP_DIR")
    if env_app_dir:
        candidates.append(Path(env_app_dir).expanduser())

    root = Path(repo_root).resolve()
    cwd = Path.cwd().resolve()
    candidates.extend(
        [
            root.parent / "TorBotApp",
            cwd / "TorBotApp",
            cwd.parent / "TorBotApp",
        ]
    )

    for candidate in candidates:
        resolved = candidate.resolve()
        if _looks_like_torbot_app(resolved):
            return resolved

    return None


def launch_torbot_app(
    repo_root: str | os.PathLike[str],
    app_dir: str | None = None,
) -> int:
    """
    Launch the optional Electron app with npm.

    Returns a process-style exit code so the CLI can exit cleanly.
    """
    torbot_app_dir = find_torbot_app(repo_root, app_dir=app_dir)
    if torbot_app_dir is None:
        print("TorBotApp is not installed or could not be found.")
        print(f"Clone it from {TORBOT_APP_REPOSITORY_URL}")
        print("Expected layout: TorBot and TorBotApp as sibling directories.")
        print("You can also set TORBOT_APP_DIR or pass --app-dir /path/to/TorBotApp.")
        return 1

    if shutil.which("npm") is None:
        print("npm is required to launch TorBotApp, but it was not found on PATH.")
        print("Install Node.js/npm, then run this command again.")
        return 1

    print(f"Starting TorBotApp from {torbot_app_dir}")
    completed = subprocess.run(["npm", "start"], cwd=str(torbot_app_dir), check=False)
    return completed.returncode
