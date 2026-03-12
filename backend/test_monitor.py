# backend/test_monitor.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from log_monitor import start_monitoring
import time

def on_event(event):
    """This function runs every time monitor finds something."""
    print(f"\n✅ EVENT CAUGHT!")
    print(f"   Type: {event['type']}")
    print(f"   IP:   {event['ip']}")
    print(f"   User: {event['user']}")
    print(f"   Time: {event['timestamp']}")

# Start monitoring
start_monitoring('./logs/simulated_auth.log', on_event)

# Keep program running for 30 seconds
print("\n[TEST] Monitor is running! Now run simulate_attack.py in another terminal...\n")
time.sleep(30)