# backend/test_detector.py

from threat_detector import ThreatDetector

# Create the detector
detector = ThreatDetector()

print("Testing Threat Detector...")
print("Sending 6 fake failed logins from same IP\n")

# Simulate 6 failed logins from same IP
for i in range(6):
    fake_event = {
        'type': 'failed_login',
        'ip': '45.33.32.156',
        'user': 'root',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }

    print(f"Sending event {i+1}...")
    alert = detector.analyze(fake_event)

    if alert:
        print(alert)  # Print the threat report
        print("\n✅ Detector is working! Attack was detected!")
        break
    else:
        print(f"   No threat yet ({i+1}/5 failures seen)")