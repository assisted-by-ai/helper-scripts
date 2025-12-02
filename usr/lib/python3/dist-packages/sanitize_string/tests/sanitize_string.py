#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring,fixme

import sys
from io import StringIO
from unittest import mock

from strip_markup.tests.strip_markup import TestStripMarkupBase
from stdisplay.tests.stdisplay import simple_escape_cases

from sanitize_string.sanitize_string import main as sanitize_string_main


class TestSanitizeString(TestStripMarkupBase):
    """
    Tests for sanitize_string.py.
    """

    maxDiff = None

    argv0: str = "sanitize-string"
    help_str: str = """\
sanitize-string: Usage: sanitize-string [--help] max_length [string]
  If no string is provided as an argument, the string is read from standard input.
  Set max_length to 'nolimit' to allow arbitrarily long strings.
"""

    def _test_args_with_exit(
        self,
        stdout_string: str,
        stderr_string: str,
        args: list[str],
        exit_code: int,
    ) -> None:
        stdout_buf: StringIO = StringIO()
        stderr_buf: StringIO = StringIO()
        args_arr: list[str] = [self.argv0, *args]
        with (
            mock.patch.object(sys, "argv", args_arr),
            mock.patch.object(sys, "stdout", stdout_buf),
            mock.patch.object(sys, "stderr", stderr_buf),
        ):
            result: int = sanitize_string_main()
        self.assertEqual(stdout_buf.getvalue(), stdout_string)
        self.assertEqual(stderr_buf.getvalue(), stderr_string)
        self.assertEqual(result, exit_code)
        stdout_buf.close()
        stderr_buf.close()

    def test_help(self) -> None:
        """
        Ensure sanitize_string.py's help output is as expected.
        """

        self._test_args(
            main_func=sanitize_string_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=self.help_str,
            args=["--help"],
        )
        self._test_args(
            main_func=sanitize_string_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=self.help_str,
            args=["-h"],
        )

    def test_usage_errors(self) -> None:
        """Ensure argument validation errors emit usage and exit non-zero."""

        error_cases: list[list[str]] = [
            [],
            ["-5"],
            ["not-a-number"],
            ["1", "2", "3"],
        ]

        for args in error_cases:
            self._test_args_with_exit(
                stdout_string="",
                stderr_string=self.help_str,
                args=args,
                exit_code=1,
            )

    def test_missing_stdin(self) -> None:
        """Verify sanitize_string exits cleanly when stdin is unavailable."""

        stdout_buf: StringIO = StringIO()
        stderr_buf: StringIO = StringIO()
        args_arr: list[str] = [self.argv0, "nolimit"]
        with (
            mock.patch.object(sys, "argv", args_arr),
            mock.patch.object(sys, "stdin", None),
            mock.patch.object(sys, "stdout", stdout_buf),
            mock.patch.object(sys, "stderr", stderr_buf),
        ):
            exit_code: int = sanitize_string_main()
        self.assertEqual(stdout_buf.getvalue(), "")
        self.assertEqual(stderr_buf.getvalue(), "")
        self.assertEqual(exit_code, 0)
        stdout_buf.close()
        stderr_buf.close()

    def test_stdin_without_reconfigure(self) -> None:
        """Ensure sanitize_string tolerates stdin objects lacking reconfigure."""

        stdout_buf: StringIO = StringIO()
        stderr_buf: StringIO = StringIO()
        stdin_buf: StringIO = StringIO("Sample input")
        args_arr: list[str] = [self.argv0, "nolimit"]
        original_pytest_module = sys.modules.pop("pytest", None)
        try:
            with (
                mock.patch.object(sys, "argv", args_arr),
                mock.patch.object(sys, "stdin", stdin_buf),
                mock.patch.object(sys, "stdout", stdout_buf),
                mock.patch.object(sys, "stderr", stderr_buf),
            ):
                exit_code: int = sanitize_string_main()
        finally:
            if original_pytest_module is not None:
                sys.modules["pytest"] = original_pytest_module
        self.assertEqual(stdout_buf.getvalue(), "Sample input")
        self.assertEqual(stderr_buf.getvalue(), "")
        self.assertEqual(exit_code, 0)
        stdout_buf.close()
        stderr_buf.close()

    def test_unreadable_stdin_raises_error(self) -> None:
        """Ensure unreadable stdin streams fail gracefully."""

        class ExplodingStdin:
            def read(self) -> str:  # pragma: no cover - invoked via main
                raise ValueError("boom")

        stdout_buf: StringIO = StringIO()
        stderr_buf: StringIO = StringIO()
        args_arr: list[str] = [self.argv0, "nolimit"]
        with (
            mock.patch.object(sys, "argv", args_arr),
            mock.patch.object(sys, "stdin", ExplodingStdin()),
            mock.patch.object(sys, "stdout", stdout_buf),
            mock.patch.object(sys, "stderr", stderr_buf),
        ):
            exit_code: int = sanitize_string_main()
        self.assertEqual(stdout_buf.getvalue(), "")
        self.assertEqual(
            stderr_buf.getvalue(),
            "sanitize-string: failed to read from standard input\n",
        )
        self.assertEqual(exit_code, 1)
        stdout_buf.close()
        stderr_buf.close()

    def test_missing_read_attribute_returns_error(self) -> None:
        """Validate stdin objects without read cause a clean failure."""

        class NoReadStdin:  # pragma: no cover - exercised indirectly
            pass

        stdout_buf: StringIO = StringIO()
        stderr_buf: StringIO = StringIO()
        args_arr: list[str] = [self.argv0, "nolimit"]
        with (
            mock.patch.object(sys, "argv", args_arr),
            mock.patch.object(sys, "stdin", NoReadStdin()),
            mock.patch.object(sys, "stdout", stdout_buf),
            mock.patch.object(sys, "stderr", stderr_buf),
        ):
            exit_code: int = sanitize_string_main()
        self.assertEqual(stdout_buf.getvalue(), "")
        self.assertEqual(
            stderr_buf.getvalue(),
            "sanitize-string: standard input is unreadable\n",
        )
        self.assertEqual(exit_code, 1)
        stdout_buf.close()
        stderr_buf.close()

    def test_safe_strings(self) -> None:
        """
        Wrapper for _test_safe_strings (from TestStripMarkup) specific to
        TestSanitizeString.
        """

        self._test_safe_strings(
            sanitize_string_main, self.argv0, pos_args_prefix=["nolimit"]
        )

    def test_markup_strings(self) -> None:
        """
        Wrapper for _test_markup_strings (from TestStripMarkup) specific to
        TestSanitizeString.
        """

        self._test_markup_strings(
            sanitize_string_main, self.argv0, pos_args_prefix=["nolimit"]
        )

    def test_malicious_markup_strings(self) -> None:
        """
        Wrapper for _test_malicious_markup_strings (from TestStripMarkup)
        specific to TestSanitizeString.
        """

        self._test_malicious_markup_strings(
            sanitize_string_main, self.argv0, pos_args_prefix=["nolimit"]
        )

    def test_simple_escape_cases(self) -> None:
        """
        Ensures sanitize_string.py correctly sanitizes escape sequences and
        Unicode.
        """

        for test_case in simple_escape_cases:
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["nolimit", test_case[0]],
            )
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["--", "nolimit", test_case[0]],
            )
            self._test_stdin(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["nolimit"],
                stdin_string=test_case[0],
            )

    def test_malicious_cases(self) -> None:
        """
        Ensures malicious HTML plus malicious Unicode plus malicious escape
        sequences are handled correctly.
        """

        ## TODO: Add more than one test case.

        test_case_list: list[tuple[str, str]] = [
            (
                """\
<html><head><script>
\N{RIGHT-TO-LEFT ISOLATE}\
\N{LEFT-TO-RIGHT ISOLATE}\
blowupWorld() \
\N{POP DIRECTIONAL ISOLATE}\
\N{LEFT-TO-RIGHT ISOLATE}\
//\
\N{POP DIRECTIONAL ISOLATE}\
\N{POP DIRECTIONAL ISOLATE} \
Won't blow up world, because it's commented :) \x1b[8mor not!\x1b[0m
</script></head><body>
<p>There really isn't bold text below, I promise!</p>
<<b>b>Not bold!<</b>/b>
</body></html>
""",
                """\

__blowupWorld() __//__ Won't blow up world, because it's commented :) \
_[8mor not!_[0m

There really isn't bold text below, I promise!
_b_Not bold!_/b_

""",
            ),
        ]

        for test_case in test_case_list:
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["nolimit", test_case[0]],
            )
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["--", "nolimit", test_case[0]],
            )
            self._test_stdin(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["nolimit"],
                stdin_string=test_case[0],
            )

    def test_long_cases(self) -> None:
        """
        Ensures sanitize-string's truncation feature works.
        """

        test_case_list: list[tuple[str, str, str]] = [
            (
                "This is a longish string.",
                "9",
                "This is a",
            ),
            (
                "This is a longish string.",
                "15",
                "This is a longi",
            ),
            ("This is a longish string.", "100", "This is a longish string."),
            (
                "This is a longish string.",
                "0",
                "",
            ),
            (
                "<p>This string is shorter than it looks.</p>",
                "36",
                "This string is shorter than it looks",
            ),
            (
                "\x1b[8mThis text is hidden.\x1b[0m",
                "16",
                "_[8mThis text is",
            ),
            (
                """\
This text is multi-line.
That is, with a newline inserted.""",
                "42",
                """\
This text is multi-line.
That is, with a n""",
            ),
        ]

        for test_case in test_case_list:
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[2],
                stderr_string="",
                args=[test_case[1], test_case[0]],
            )
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[2],
                stderr_string="",
                args=["--", test_case[1], test_case[0]],
            )
            self._test_stdin(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[2],
                stderr_string="",
                args=[test_case[1]],
                stdin_string=test_case[0],
            )
