# backend/test_full_pipeline.py

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_database
from log_monitor import start_monitoring
from threat_detector import ThreatDetector
from playbook_engine import dispatch

# Initialize database
init_database()

# Create detector
detector = ThreatDetector()

def on_event(event):
    """Full pipeline — monitor → detect → respond."""

    # Step 1: Detect threat
    alert = detector.analyze(event)

    # Step 2: If threat found → run playbook
    if alert:
        print(f"\n🚨 THREAT DETECTED — launching playbook...")
        result = dispatch(alert)

        if result:
            print(f"\n✅ FULL PIPELINE COMPLETE!")
            print(f"   Check your Slack for the alert!")
            print(f"   Check soar.db for the saved incident!")

# Start monitoring
start_monitoring('./logs/simulated_auth.log', on_event)

print("="*50)
print("🛡️  SOAR FULL PIPELINE RUNNING")
print("="*50)
print("Monitor  ✅ watching logs")
print("Detector ✅ analyzing events")
print("Playbook ✅ ready to respond")
print("Database ✅ ready to save")
print("Slack    ✅ ready to alert")
print("="*50)
print("\nRun simulate_attack.py in another terminal!\n")

# Keep running
time.sleep(120)