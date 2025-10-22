"""Tests for set-keyboard-layout helper functions."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _create_stub(command_dir: Path, name: str, contents: str) -> None:
    script_path = command_dir / name
    script_path.write_text(contents, encoding="utf-8")
    script_path.chmod(0o755)


def test_ephemeral_labwc_config_preserves_existing_content(tmp_path: Path) -> None:
    """Ensure non-persistent updates keep pre-existing config lines."""

    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()

    _create_stub(
        stub_dir,
        "safe-rm",
        "#!/bin/bash\nset -e\nrm \"$@\"\n",
    )

    _create_stub(
        stub_dir,
        "localectl",
        (
            "#!/bin/bash\n"
            "set -e\n"
            "case \"$1\" in\n"
            "  list-x11-keymap-layouts)\n"
            "    printf 'us\\n'\n"
            "    ;;\n"
            "  list-x11-keymap-variants)\n"
            "    exit 0\n"
            "    ;;\n"
            "  list-x11-keymap-options)\n"
            "    exit 0\n"
            "    ;;\n"
            "  *)\n"
            "    echo 'localectl stub: unsupported command' >&2\n"
            "    exit 1\n"
            "    ;;\n"
            "esac\n"
        ),
    )

    _create_stub(
        stub_dir,
        "overwrite",
        (
            "#!/bin/bash\n"
            "set -e\n"
            "if [ \"$#\" -ne 2 ]; then\n"
            "  echo 'overwrite stub: unexpected arguments' >&2\n"
            "  exit 1\n"
            "fi\n"
            "printf '%s' \"$2\" > \"$1\"\n"
        ),
    )

    env = os.environ.copy()
    env["PATH"] = os.pathsep.join(
        (
            str(stub_dir),
            str(REPO_ROOT / "usr/bin"),
            env.get("PATH", ""),
        )
    )
    env["PYTHONPATH"] = os.pathsep.join(
        (
            str(REPO_ROOT / "usr/lib/python3/dist-packages"),
            env.get("PYTHONPATH", ""),
        )
    )

    home_dir = tmp_path / "home"
    env["HOME"] = str(home_dir)

    labwc_env_path = home_dir / ".config" / "labwc" / "environment"
    labwc_env_path.parent.mkdir(parents=True, exist_ok=True)
    original_contents = "EXTRA_VAR=1\nXKB_DEFAULT_LAYOUT=us\n"
    labwc_env_path.write_text(original_contents, encoding="utf-8")

    command = (
        f"source '{REPO_ROOT / 'usr/libexec/helper-scripts/set-keyboard-layout.sh'}'"
        " && set_labwc_keymap --no-reload us"
    )

    result = subprocess.run(
        ["bash", "-c", command],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "EXTRA_VAR=1" in result.stderr
    assert labwc_env_path.read_text(encoding="utf-8") == original_contents
