# backend/test_intel.py
# Replace your test IPs with these

from threat_intel import check_ip_reputation

# These are well known bad IPs
test_ips = [
    "185.220.101.1",    # Tor exit node — almost always flagged
    "89.234.157.254",   # Known malicious
    "171.25.193.77",    # Tor exit — in most lists
    "192.168.1.100",    # Private IP — should stay CLEAN
]

for ip in test_ips:
    result = check_ip_reputation(ip)
    print(f"\nIP: {ip}")
    print(f"VERDICT:  {result['verdict']}")
    print(f"SCORE:    {result['abuse_score']}/100")
    print(f"SOURCES:  {result['sources_found']}/{result['sources_checked']} flagged")
    print(f"SUMMARY:  {result['summary']}")
    print("─" * 50)