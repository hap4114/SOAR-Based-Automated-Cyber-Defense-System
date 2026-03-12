# backend/threat_detector.py

from collections import defaultdict
from datetime import datetime, timedelta

class ThreatAlert:
    """
    This is like a report card for an attack.
    When an attack is detected, we create one of these
    and pass it to the playbook engine.
    """
    def __init__(self, threat_type, severity, source_ip, details, event_count):
        self.threat_type = threat_type    # e.g. 'BRUTE_FORCE'
        self.severity = severity          # e.g. 'HIGH'
        self.source_ip = source_ip        # e.g. '45.33.32.156'
        self.details = details            # e.g. '6 failed logins in 60s'
        self.event_count = event_count    # e.g. 6
        self.timestamp = datetime.now().isoformat()

    def __str__(self):
        return (
            f"\n{'='*50}"
            f"\n🚨 THREAT DETECTED!"
            f"\n   Type:     {self.threat_type}"
            f"\n   Severity: {self.severity}"
            f"\n   IP:       {self.source_ip}"
            f"\n   Details:  {self.details}"
            f"\n   Time:     {self.timestamp}"
            f"\n{'='*50}"
        )


class ThreatDetector:
    """
    The brain of the SOAR system.
    Receives events one by one.
    Remembers recent events per IP.
    Decides if something is an attack.
    """

    def __init__(self):
        # Dictionary to store events per IP
        # Example:
        # {
        #   '45.33.32.156': [event1, event2, event3],
        #   '192.168.1.1':  [event1]
        # }
        self.ip_events = defaultdict(list)

        # Settings
        self.WINDOW_SECONDS = 60        # Look at last 60 seconds
        self.BRUTE_FORCE_THRESHOLD = 5  # 5 failures = attack

    def _clean_old_events(self, ip):
        """
        Remove events older than 60 seconds for this IP.
        We only care about RECENT events.

        Example:
        Events at: 3:00, 3:01, 3:02, 3:10
        If it's now 3:05 → remove 3:00 event (older than 60s... wait)
        Actually if window is 60s and now is 3:05:
        Keep: 3:01, 3:02 (within 60s)
        Remove: 3:00 (older than 60s... barely)
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.WINDOW_SECONDS)

        # Keep only events newer than cutoff time
        self.ip_events[ip] = [
            event for event in self.ip_events[ip]
            if datetime.fromisoformat(event['timestamp']) > cutoff
        ]

    def analyze(self, event):
        """
        Main function. Called for every new event.
        Returns a ThreatAlert if attack detected.
        Returns None if everything is normal.
        """
        ip = event['ip']

        # Step 1: Remember this event
        self.ip_events[ip].append(event)

        # Step 2: Remove old events (older than 60 seconds)
        self._clean_old_events(ip)

        # Step 3: Apply detection rules

        # ─────────────────────────────────────
        # RULE 1: Brute Force Detection
        # If same IP fails login 5+ times in 60s
        # ─────────────────────────────────────
        if event['type'] == 'failed_login':

            # Count how many failed logins from this IP
            failed_logins = [
                e for e in self.ip_events[ip]
                if e['type'] == 'failed_login'
            ]
            fail_count = len(failed_logins)

            print(f"[DETECTOR] {ip} has {fail_count} failed logins in last 60s")

            if fail_count >= self.BRUTE_FORCE_THRESHOLD:
                return ThreatAlert(
                    threat_type='BRUTE_FORCE',
                    severity='HIGH',
                    source_ip=ip,
                    details=f"{fail_count} failed logins in {self.WINDOW_SECONDS} seconds",
                    event_count=fail_count
                )

        # ─────────────────────────────────────
        # RULE 2: Successful login after failures
        # Someone failed many times then got in
        # That's suspicious! Maybe they cracked it
        # ─────────────────────────────────────
        if event['type'] == 'success_login':

            # How many failures before this success?
            failed_before = [
                e for e in self.ip_events[ip]
                if e['type'] == 'failed_login'
            ]

            if len(failed_before) >= 3:
                return ThreatAlert(
                    threat_type='CREDENTIAL_STUFFING',
                    severity='CRITICAL',
                    source_ip=ip,
                    details=f"Successful login after {len(failed_before)} failures — possible break-in!",
                    event_count=len(failed_before)
                )

        # No threat detected for this event
        return None