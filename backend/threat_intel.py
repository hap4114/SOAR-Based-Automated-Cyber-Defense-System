# backend/threat_intel.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────
# PART 1: Load all local datasets into memory
# Done ONCE when program starts — fast lookup later
# ─────────────────────────────────────────────────

def load_ipsum():
    """
    ipsum format:
    45.33.32.156    8
    IP = key, score = value
    Higher score = more dangerous
    """
    data = {}
    path = "./backend/data/ipsum.txt"

    if not os.path.exists(path):
        print("[INTEL] ipsum dataset not found")
        return data

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 1:
                ip = parts[0]
                score = int(parts[1]) if len(parts) > 1 else 1
                data[ip] = score

    print(f"[INTEL] ✅ Loaded ipsum: {len(data)} IPs")
    return data


def load_emerging_threats():
    """
    Emerging threats format:
    One IP per line
    1.10.16.0
    1.19.0.0
    """
    data = set()
    path = "./backend/data/emerging_threats.txt"

    if not os.path.exists(path):
        print("[INTEL] Emerging Threats dataset not found")
        return data

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            data.add(line)

    print(f"[INTEL] ✅ Loaded Emerging Threats: {len(data)} IPs")
    return data


def load_firehol():
    """
    Firehol format:
    Mix of single IPs and IP ranges
    We only use single IPs for simplicity
    """
    data = set()
    path = "./backend/data/firehol.txt"

    if not os.path.exists(path):
        print("[INTEL] Firehol dataset not found")
        return data

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Skip IP ranges (contain /)
            if '/' not in line:
                data.add(line)

    print(f"[INTEL] ✅ Loaded Firehol: {len(data)} IPs")
    return data


# Load everything ONCE when program starts
print("[INTEL] Loading all threat intelligence datasets...")
IPSUM_DATA = load_ipsum()
EMERGING_THREATS_DATA = load_emerging_threats()
FIREHOL_DATA = load_firehol()
print("[INTEL] All datasets loaded and ready!\n")


# ─────────────────────────────────────────────────
# PART 2: Check each source individually
# ─────────────────────────────────────────────────

def check_abuseipdb(ip):
    """Check AbuseIPDB live API."""
    api_key = os.getenv('ABUSEIPDB_API_KEY')
    if not api_key:
        return None

    try:
        response = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={
                'Accept': 'application/json',
                'Key': api_key
            },
            params={
                'ipAddress': ip,
                'maxAgeInDays': 90
            },
            timeout=5
        )

        if response.status_code == 429:
            print("[INTEL] AbuseIPDB limit reached")
            return None

        if response.status_code == 401:
            print("[INTEL] AbuseIPDB invalid key")
            return None

        data = response.json()['data']
        return {
            'source': 'AbuseIPDB',
            'found': data['abuseConfidenceScore'] > 0,
            'score': data['abuseConfidenceScore'],      # 0-100
            'country': data.get('countryCode', 'Unknown'),
            'details': f"{data['totalReports']} reports on AbuseIPDB"
        }

    except Exception as e:
        print(f"[INTEL] AbuseIPDB error: {e}")
        return None


def check_ipsum(ip):
    """Check ipsum local dataset."""
    if ip in IPSUM_DATA:
        raw_score = IPSUM_DATA[ip]
        return {
            'source': 'ipsum',
            'found': True,
            'score': min(raw_score * 10, 100),  # Convert to 0-100
            'country': 'Unknown',
            'details': f"Reported by {raw_score} threat sources in ipsum"
        }
    return {
        'source': 'ipsum',
        'found': False,
        'score': 0,
        'country': 'Unknown',
        'details': 'Not found in ipsum'
    }


def check_emerging_threats(ip):
    """Check Emerging Threats local dataset."""
    found = ip in EMERGING_THREATS_DATA
    return {
        'source': 'Emerging Threats',
        'found': found,
        'score': 80 if found else 0,   # If found = high score
        'country': 'Unknown',
        'details': 'Found in Emerging Threats list' if found else 'Not found in Emerging Threats'
    }


def check_firehol(ip):
    """Check Firehol local dataset."""
    found = ip in FIREHOL_DATA
    return {
        'source': 'Firehol Level 1',
        'found': found,
        'score': 90 if found else 0,   # Firehol = very high confidence
        'country': 'Unknown',
        'details': 'Found in Firehol Level 1 (highest confidence)' if found else 'Not found in Firehol'
    }


# ─────────────────────────────────────────────────
# PART 3: Combine all results into final verdict
# ─────────────────────────────────────────────────

def check_ip_reputation(ip):
    """
    THE MAIN FUNCTION.
    Checks ALL sources.
    Combines results into one final verdict.
    Always returns a result — never crashes.
    """
    print(f"\n[INTEL] ═══ Checking {ip} across all sources ═══")

    results = []

    # Check all sources
    sources = [
        ("AbuseIPDB",        check_abuseipdb),
        ("ipsum",            check_ipsum),
        ("Emerging Threats", check_emerging_threats),
        ("Firehol",          check_firehol),
    ]

    for name, check_fn in sources:
        result = check_fn(ip)
        if result:
            results.append(result)
            status = "🔴 FOUND" if result['found'] else "🟢 Clean"
            print(f"[INTEL]   {name:<20} → {status} (score: {result['score']})")

    # ── Calculate final combined score ──
    # Average of all scores that found something
    found_results = [r for r in results if r['found']]
    sources_found = len(found_results)

    if sources_found == 0:
        # Nobody found anything suspicious
        final_score = 0
        verdict = "CLEAN"
        confidence = "HIGH"
    else:
        # Average score from sources that found it
        avg_score = sum(r['score'] for r in found_results) / sources_found

        # Bonus points for multiple sources agreeing
        # 1 source = base score
        # 2 sources = +10 bonus
        # 3 sources = +20 bonus
        # 4 sources = +30 bonus
        consensus_bonus = (sources_found - 1) * 10
        final_score = min(avg_score + consensus_bonus, 100)

        verdict = "DANGEROUS" if final_score > 70 else "SUSPICIOUS" if final_score > 30 else "LOW_RISK"
        confidence = "HIGH" if sources_found >= 3 else "MEDIUM" if sources_found == 2 else "LOW"

    # Get country from AbuseIPDB if available
    country = next(
        (r['country'] for r in results if r.get('country') != 'Unknown'),
        'Unknown'
    )

    # Build final result
    final = {
        'ip': ip,
        'abuse_score': round(final_score),
        'verdict': verdict,
        'confidence': confidence,
        'country': country,
        'sources_checked': len(results),
        'sources_found': sources_found,
        'is_known_attacker': final_score > 30,
        'breakdown': results,   # Individual source results
        'summary': build_summary(ip, results, final_score, verdict, confidence)
    }

    print(f"[INTEL] ───────────────────────────────────────")
    print(f"[INTEL]   Final Score:  {round(final_score)}/100")
    print(f"[INTEL]   Verdict:      {verdict}")
    print(f"[INTEL]   Confidence:   {confidence} ({sources_found}/{len(results)} sources flagged)")
    print(f"[INTEL] ═══════════════════════════════════════\n")

    return final


def build_summary(ip, results, score, verdict, confidence):
    """Build a human readable summary for Slack alerts."""
    found_in = [r['source'] for r in results if r['found']]

    if not found_in:
        return f"{ip} — Not found in any threat database"

    sources_str = ", ".join(found_in)
    return (
        f"{ip} flagged by: {sources_str} | "
        f"Score: {round(score)}/100 | "
        f"Verdict: {verdict} | "
        f"Confidence: {confidence}"
    )