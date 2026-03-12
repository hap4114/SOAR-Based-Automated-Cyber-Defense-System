# backend/log_monitor.py

import re
import time
import threading
from datetime import datetime

def parse_log_line(line):
    """
    Reads one line from the log file.
    Extracts useful info from it.
    Returns a dictionary or None.
    """

    # Pattern 1: Failed login attempt
    # Looking for lines like:
    # "Failed password for root from 45.33.32.156 port 22"
    ssh_fail = re.search(
        r'Failed password for (\S+) from (\S+) port', line
    )
    if ssh_fail:
        return {
            'type': 'failed_login',
            'user': ssh_fail.group(1),   # e.g. "root"
            'ip': ssh_fail.group(2),     # e.g. "45.33.32.156"
            'timestamp': datetime.now().isoformat(),
            'raw': line.strip()
        }

    # Pattern 2: Successful login
    # Looking for lines like:
    # "Accepted password for john from 192.168.1.1"
    ssh_success = re.search(
        r'Accepted password for (\S+) from (\S+)', line
    )
    if ssh_success:
        return {
            'type': 'success_login',
            'user': ssh_success.group(1),
            'ip': ssh_success.group(2),
            'timestamp': datetime.now().isoformat(),
            'raw': line.strip()
        }

    # If line doesn't match anything useful
    return None


def tail_log_file(filepath, callback):
    """
    Follows a log file in real time.
    Like 'tail -f' command in Linux.
    Calls callback() every time a new event is found.
    """
    print(f"[MONITOR] Opening log file: {filepath}")

    with open(filepath, 'r') as f:
        # Jump to END of file first
        # So we only read NEW lines, not old ones
        f.seek(0, 2)
        print("[MONITOR] Watching for new events...")

        while True:
            line = f.readline()

            if not line:
                # No new line yet — wait a little and try again
                time.sleep(0.1)
                continue

            # New line found! Try to parse it
            event = parse_log_line(line)

            if event:
                print(f"[MONITOR] New event detected: {event['type']} from {event['ip']}")
                callback(event)  # Send event to threat detector


def start_monitoring(log_path, on_event):
    """
    Starts the log monitor in a background thread.
    So it runs silently while other code runs too.
    """
    thread = threading.Thread(
        target=tail_log_file,
        args=(log_path, on_event),
        daemon=True  # Stops automatically when main program stops
    )
    thread.start()
    print(f"[MONITOR] Started monitoring: {log_path}")