# Test Run Report

Command: ./run-tests

Date: 2025-12-02 04:58:15Z

Result: Failed (10 failures, 12 passed)

Notes:
- Failing cases are primarily in stdisplay utilities (stcat, stcatn, stecho, stprint, stsponge, sttee).
- Failures include unexpected ANSI escape sequences that were not sanitized and missing terminfo entries (xterm-direct, xterm-old).
- Terminfo lookup gaps suggest an environment/configuration issue rather than a product bug; rerun after installing the required entries to confirm.
- See test log in the run output for full details.
