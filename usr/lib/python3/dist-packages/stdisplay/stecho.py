#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""Safely print argument to stdout with echo's formatting."""

import sys
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """Safely print argument to stdout with echo's formatting."""
    if len(sys.argv) > 1:
        untrusted_text = " ".join(sys.argv[1:])
        sys.stdout.write(stdisplay(untrusted_text))
    sys.stdout.write("\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
