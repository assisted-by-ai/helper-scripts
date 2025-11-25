#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""Safely print stdin to stdout and file without following symlinks."""
import os
from sys import argv, stdin, stdout, modules
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """Safely print stdin to stdout and file."""
    # https://github.com/pytest-dev/pytest/issues/4843
    if "pytest" not in modules and stdin is not None:
        stdin.reconfigure(errors="replace")  # type: ignore
    output_files = []
    try:
        if len(argv) > 1:
            for file_arg in argv[1:]:
                fd = os.open(
                    file_arg,
                    os.O_CREAT | os.O_WRONLY | os.O_TRUNC | os.O_NOFOLLOW,
                    0o600,
                )
                output_files.append(os.fdopen(fd, mode="w", encoding="ascii"))
        if stdin is not None:
            for untrusted_text in stdin:
                rendered_text = stdisplay(untrusted_text)
                stdout.write(rendered_text)
                for output_file in output_files:
                    output_file.write(rendered_text)
            stdout.flush()
            for output_file in output_files:
                output_file.flush()
    finally:
        for output_file in output_files:
            output_file.close()


if __name__ == "__main__":
    main()
