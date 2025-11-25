#!/usr/bin/env python3
# pylint: disable=missing-module-docstring

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

import importlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import stdisplay.tests


class TestSTTee(stdisplay.tests.TestSTBase):
    """
    Test sttee
    """

    def setUp(self) -> None:
        self.module = "sttee"
        super().setUp()

    def test_sttee(self) -> None:
        """
        Test sttee.
        """
        self.assertEqual("", self._test_util())
        self.assertEqual("", self._test_util(stdin=""))
        self.assertEqual("stdin", self._test_util(stdin="stdin"))
        # Empty stdin with file argument.
        self.assertEqual("", self._test_util(argv=[self.tmpfiles["fill"]]))
        self.assertEqual(
            "",
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        # Stdin sanitization and writing to file.
        self.assertEqual(
            self.text_dirty_sanitized,
            self._test_util(
                stdin=self.text_dirty, argv=[self.tmpfiles["fill"]]
            ),
        )
        self.assertEqual(
            self.text_dirty_sanitized,
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        # Stdin sanitization and writing to multiple files.
        self.assertEqual(
            self.text_dirty_sanitized,
            self._test_util(
                stdin=self.text_dirty,
                argv=[self.tmpfiles["fill"], self.tmpfiles["fill2"]],
            ),
        )
        self.assertEqual(
            self.text_dirty_sanitized,
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        self.assertEqual(
            self.text_dirty_sanitized,
            Path(self.tmpfiles["fill2"]).read_text(encoding="utf-8"),
        )

    def test_sttee_replaces_invalid_bytes(self) -> None:
        """Invalid bytes are surfaced as sanitized underscores."""

        output_path = Path(self.tmpfiles["fill"])
        invalid_bytes = b"a\xffb\n"
        stdout_capture = io.StringIO()
        pytest_module = sys.modules.pop("pytest", None)
        try:
            with patch.object(sys, "argv", ["sttee.py", str(output_path)]), patch(
                "sys.stdin",
                io.TextIOWrapper(io.BytesIO(invalid_bytes), encoding="utf-8"),
            ), patch("sys.stdout", stdout_capture):
                self._del_module()
                importlib.import_module("stdisplay.sttee").main()
        finally:
            if pytest_module is not None:
                sys.modules["pytest"] = pytest_module

        self.assertEqual("a_b\n", stdout_capture.getvalue())
        self.assertEqual("a_b\n", output_path.read_text(encoding="ascii"))

    def test_sttee_sanitizes_control_and_bidi(self) -> None:
        """Dangerous control characters are sanitized before writing."""

        output_path = Path(self.tmpfiles["fill"])
        stdout_capture = io.StringIO()
        with patch.object(
            sys, "argv", ["sttee.py", str(output_path)]
        ), patch("sys.stdin", io.StringIO(self.text_malicious)), patch(
            "sys.stdout", stdout_capture
        ):
            self._del_module()
            importlib.import_module("stdisplay.sttee").main()

        self.assertEqual(self.text_malicious_sanitized, stdout_capture.getvalue())
        self.assertEqual(
            self.text_malicious_sanitized,
            output_path.read_text(encoding="ascii"),
        )


if __name__ == "__main__":
    unittest.main()
