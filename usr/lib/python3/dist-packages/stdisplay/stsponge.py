#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""Safely print stdin to stdout or file."""

import os
from sys import argv, stdin, stdout, modules
from tempfile import NamedTemporaryFile
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """Safely print stdin to stdout or file."""
    # https://github.com/pytest-dev/pytest/issues/4843
    if "pytest" not in modules and stdin is not None:
        stdin.reconfigure(errors="replace")  # type: ignore
    untrusted_text_list = []
    if stdin is not None:
        for untrusted_text in stdin:
            untrusted_text_list.append(untrusted_text)
    if len(argv) == 1:
        stdout.write(stdisplay("".join(untrusted_text_list)))
        stdout.flush()
    else:
        with NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(stdisplay("".join(untrusted_text_list)))
            temp_file.flush()
            temp_path = temp_file.name
        try:
            with open(temp_path, "rb") as source_file:
                content = source_file.read()
            for file in argv[1:]:
                fd = os.open(
                    file,
                    os.O_CREAT | os.O_WRONLY | os.O_TRUNC | os.O_NOFOLLOW,
                    0o600,
                )
                with os.fdopen(fd, "wb") as destination_file:
                    destination_file.write(content)
                    destination_file.flush()
                    os.fchmod(destination_file.fileno(), 0o600)
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    main()
