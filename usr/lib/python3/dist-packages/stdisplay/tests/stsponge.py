#!/usr/bin/env python3
# pylint: disable=missing-module-docstring disable=duplicate-code

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


class TestSTSponge(stdisplay.tests.TestSTBase):
    """
    Test stsponge.
    """

    def setUp(self) -> None:
        self.module = "stsponge"
        super().setUp()

    def test_stsponge(self) -> None:
        """
        Test stsponge.
        """
        self.assertEqual("", self._test_util())
        self.assertEqual("", self._test_util(stdin=""))
        self.assertEqual("stdin", self._test_util(stdin="stdin"))
        # Empty stdin with file argument produces empty stdout and file.
        self.assertEqual("", self._test_util(argv=[self.tmpfiles["fill"]]))
        self.assertEqual(
            "",
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        # Empty stdout when writing to file and file sanitization.
        self.assertEqual(
            "",
            self._test_util(
                stdin=self.text_dirty, argv=[self.tmpfiles["fill"]]
            ),
        )
        self.assertEqual(
            self.text_dirty_sanitized,
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        # Empty stdout when writing to multiple files and its sanitization.
        self.assertEqual(
            "",
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

    def test_stsponge_replaces_invalid_bytes(self) -> None:
        """Invalid bytes are sanitized for stdout and files."""

        output_path = Path(self.tmpfiles["fill"])
        invalid_bytes = b"a\xffb\n"
        stdout_capture = io.StringIO()
        pytest_module = sys.modules.pop("pytest", None)
        try:
            with patch.object(sys, "argv", ["stsponge.py", str(output_path)]), patch(
                "sys.stdin",
                io.TextIOWrapper(io.BytesIO(invalid_bytes), encoding="utf-8"),
            ), patch("sys.stdout", stdout_capture):
                self._del_module()
                importlib.import_module("stdisplay.stsponge").main()
        finally:
            if pytest_module is not None:
                sys.modules["pytest"] = pytest_module

        self.assertEqual("", stdout_capture.getvalue())
        self.assertEqual("a_b\n", output_path.read_text(encoding="ascii"))

        stdout_capture = io.StringIO()
        pytest_module = sys.modules.pop("pytest", None)
        try:
            with patch.object(sys, "argv", ["stsponge.py"]), patch(
                "sys.stdin",
                io.TextIOWrapper(io.BytesIO(invalid_bytes), encoding="utf-8"),
            ), patch("sys.stdout", stdout_capture):
                self._del_module()
                importlib.import_module("stdisplay.stsponge").main()
        finally:
            if pytest_module is not None:
                sys.modules["pytest"] = pytest_module

        self.assertEqual("a_b\n", stdout_capture.getvalue())

    def test_stsponge_sanitizes_control_and_bidi(self) -> None:
        """Control and bidi characters are sanitized in outputs."""

        output_path = Path(self.tmpfiles["fill"])
        stdout_capture = io.StringIO()
        with patch.object(sys, "argv", ["stsponge.py", str(output_path)]), patch(
            "sys.stdin", io.StringIO(self.text_malicious)
        ), patch("sys.stdout", stdout_capture):
            self._del_module()
            importlib.import_module("stdisplay.stsponge").main()

        self.assertEqual("", stdout_capture.getvalue())
        self.assertEqual(
            self.text_malicious_sanitized,
            output_path.read_text(encoding="utf-8"),
        )

        stdout_capture = io.StringIO()
        with patch.object(sys, "argv", ["stsponge.py"]), patch(
            "sys.stdin", io.StringIO(self.text_malicious)
        ), patch("sys.stdout", stdout_capture):
            self._del_module()
            importlib.import_module("stdisplay.stsponge").main()

        self.assertEqual(self.text_malicious_sanitized, stdout_capture.getvalue())


if __name__ == "__main__":
    unittest.main()
