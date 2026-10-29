# log_util.py
# Homemade logger. Modernised 2025: removed permanently-dead debug() branch.

import time

LOG_LINES: list[str] = []    # module-level buffer, shared by all callers


def log(message: str) -> None:
    """Timestamp and buffer a message, and print it."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def flush_log(path: str) -> None:
    """Append buffered log lines to the log file and clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
