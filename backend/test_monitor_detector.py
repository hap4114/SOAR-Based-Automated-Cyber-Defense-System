# backend/test_monitor_detector.py

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from log_monitor import start_monitoring
from threat_detector import ThreatDetector

# Create detector
detector = ThreatDetector()

def on_event(event):
    """
    Called by log monitor for every new event.
    Now passes it to the threat detector too!
    """
    print(f"\n[MONITOR] Event: {event['type']} from {event['ip']}")

    # Pass event to detector
    alert = detector.analyze(event)

    # If detector found an attack
    if alert:
        print(alert)
        print("\n🚨 ATTACK DETECTED! Next step: run the playbook!")

# Start monitoring
start_monitoring('./logs/simulated_auth.log', on_event)

print("[SYSTEM] Monitor + Detector running!")
print("[SYSTEM] Run simulate_attack.py in another terminal\n")

# Keep running
time.sleep(60)