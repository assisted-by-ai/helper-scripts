from pathlib import Path
import subprocess
import os
import pty

UNICODE_SHOW = Path(__file__).resolve().parents[1] / "usr/bin" / "unicode-show"


def run_unicode_show(text: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(UNICODE_SHOW)],
        input=text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_unicode_show_file(path: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(UNICODE_SHOW), str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_unicode_show_tty(text: str, env: dict[str, str]) -> tuple[int, bytes, bytes]:
    """Run unicode-show with stdout attached to a pty to simulate a TTY."""

    master_fd, slave_fd = pty.openpty()
    try:
        proc = subprocess.run(
            [str(UNICODE_SHOW)],
            input=text.encode("utf-8"),
            stdout=slave_fd,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )
        os.close(slave_fd)
        stdout = os.read(master_fd, 10_000)
        return proc.returncode, stdout, proc.stderr
    finally:
        try:
            os.close(master_fd)
        except OSError:
            pass


def test_flags_ascii_control_characters():
    controls = ["\x00", "\x07", "\x1b"]
    for control in controls:
        proc = run_unicode_show(f"start{control}end\n")
        output = proc.stdout.decode("utf-8")
        assert proc.returncode == 1
        assert f"[U+{ord(control):04X}]" in output


def test_flags_unicode_format_controls():
    format_chars = ["\u200b", "\u202e"]
    for char in format_chars:
        proc = run_unicode_show(f"pre{char}post\n")
        output = proc.stdout.decode("utf-8")
        assert proc.returncode == 1
        assert f"[U+{ord(char):04X}]" in output


def test_trailing_whitespace_is_reported():
    proc = run_unicode_show("space-trailing \n\ttab-trailing\t\n")
    output = proc.stdout.decode("utf-8")
    assert proc.returncode == 1
    assert "[U+0020]" in output
    assert "[U+0009]" in output


def test_trailing_whitespace_descriptions_are_visible():
    proc = run_unicode_show("space-trailing \n\ttab-trailing\t\n")
    lines = proc.stdout.decode("utf-8").splitlines()

    assert proc.returncode == 1
    assert any("-> ' '" in line for line in lines)
    assert any("-> '\\t'" in line for line in lines)


def test_ascii_only_content_is_clean():
    proc = run_unicode_show("plain ascii text 123 !?\nline two\n")
    assert proc.returncode == 0
    assert proc.stdout == b""


def test_carriage_returns_are_surfaced():
    proc = run_unicode_show("line with\rcarriage return\n")
    output = proc.stdout.decode("utf-8")
    assert proc.returncode == 1
    assert "[U+000D]" in output


def test_invalid_utf8_input_is_an_error(tmp_path: Path):
    bad_file = tmp_path / "bad.txt"
    bad_file.write_bytes(b"valid line\n\xc3")  # Truncated UTF-8 sequence

    proc = run_unicode_show_file(bad_file)

    assert proc.returncode == 2
    assert proc.stdout == b""
    assert "Unicode decode error" in proc.stderr.decode("utf-8")


def test_nocolor_disables_output_colors_when_set_empty():
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
    env["NOCOLOR"] = ""  # Presence alone should disable colors

    returncode, stdout, stderr = run_unicode_show_tty("snowman: \u2603\n", env=env)

    assert returncode == 1
    assert b"\x1b[" not in stdout  # No ANSI escape sequences
    assert b"[U+2603]" in stdout
    assert stderr == b""


def test_no_color_standard_env_var_disables_colors():
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
    env["NO_COLOR"] = "1"  # Standard opt-out variable should disable colors

    returncode, stdout, stderr = run_unicode_show_tty("rocket: \U0001F680\n", env=env)

    assert returncode == 1
    assert b"\x1b[" not in stdout
    assert b"[U+1F680]" in stdout
    assert stderr == b""
