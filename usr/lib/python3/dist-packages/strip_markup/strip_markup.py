#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

"""
strip_markup.py: Strips HTML-like markup from a string.
"""

import sys
from .strip_markup_lib import strip_markup


def print_usage() -> None:
    """
    Prints usage information.
    """

    print(
        "strip-markup: Usage: strip-markup [--help] [string]\n"
        + "  If no string is provided as an argument, the string is read from "
        + "standard input.",
        file=sys.stderr,
    )


MAX_INPUT_BYTES = 1024 * 1024


def main() -> int:
    """
    Main function.
    """

    untrusted_string: str | None = None

    ## Process arguments
    if len(sys.argv) > 1:
        ## Parse options
        arg_list: list[str] = sys.argv[1:]
        while len(arg_list) > 0:
            arg = arg_list[0]
            # pylint: disable=no-else-return
            if arg in ("--help", "-h"):
                print_usage()
                return 0
            elif arg == "--":
                arg_list.pop(0)
                break
            else:
                break

        ## Parse positional arguments
        if len(arg_list) > 1:
            print_usage()
            return 1
        untrusted_string = arg_list[0]
        if len(untrusted_string.encode()) > MAX_INPUT_BYTES:
            print(
                f"strip-markup: input exceeds maximum size of {MAX_INPUT_BYTES} bytes.",
                file=sys.stderr,
            )
            return 1

    ## Read untrusted_string from stdin if needed
    if untrusted_string is None:
        if sys.stdin is not None:
            if hasattr(sys.stdin, "buffer"):
                raw_stdin = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
                if len(raw_stdin) > MAX_INPUT_BYTES:
                    print(
                        f"strip-markup: input exceeds maximum size of {MAX_INPUT_BYTES} bytes.",
                        file=sys.stderr,
                    )
                    return 1
                encoding = getattr(sys.stdin, "encoding", None) or "utf-8"
                untrusted_string = raw_stdin.decode(encoding, errors="ignore")
            else:
                if "pytest" not in sys.modules and hasattr(sys.stdin, "reconfigure"):
                    sys.stdin.reconfigure(errors="ignore")  # type: ignore
                untrusted_string = sys.stdin.read(MAX_INPUT_BYTES + 1)
                if len(untrusted_string.encode()) > MAX_INPUT_BYTES:
                    print(
                        f"strip-markup: input exceeds maximum size of {MAX_INPUT_BYTES} bytes.",
                        file=sys.stderr,
                    )
                    return 1
        else:
            ## No way to get an untrusted string, print nothing and
            ## exit successfully
            return 0

    ## Sanitize and print
    sys.stdout.write(strip_markup(untrusted_string))
    return 0


if __name__ == "__main__":
    main()
