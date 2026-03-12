# backend/playbook_engine.py

from backend.response_actions import block_ip_firewall, send_slack_alert
from backend.threat_intel import check_ip_reputation
from backend.database import save_incident, save_blocked_ip

# Track already processed alerts
# So we don't run playbook twice for same IP
processed_alerts = set()


def run_brute_force_playbook(alert):
    """
    Playbook for BRUTE_FORCE attacks.

    Steps:
    1. Check threat intelligence (all 4 sources)
    2. Block IP in firewall
    3. Send Slack alert
    4. Save to database
    """
    print(f"\n[PLAYBOOK] {'='*45}")
    print(f"[PLAYBOOK] Running BRUTE_FORCE playbook")
    print(f"[PLAYBOOK] Target IP: {alert.source_ip}")
    print(f"[PLAYBOOK] {'='*45}")

    # ── Step 1: Threat Intelligence ──
    print(f"\n[PLAYBOOK] Step 1/4: Checking threat intelligence...")
    intel = check_ip_reputation(alert.source_ip)

    # ── Step 2: Block IP ──
    print(f"\n[PLAYBOOK] Step 2/4: Blocking IP in firewall...")
    blocked = block_ip_firewall(alert.source_ip)
    action = "BLOCKED" if blocked else "ALERTED_ONLY"

    # ── Step 3: Send Slack Alert ──
    print(f"\n[PLAYBOOK] Step 3/4: Sending Slack alert...")
    send_slack_alert(alert, intel, action)

    # ── Step 4: Save to Database ──
    print(f"\n[PLAYBOOK] Step 4/4: Saving to database...")
    save_incident(alert, action, intel)

    if blocked:
        save_blocked_ip(alert.source_ip, alert.threat_type, intel)

    # ── Summary ──
    print(f"\n[PLAYBOOK] {'='*45}")
    print(f"[PLAYBOOK] ✅ PLAYBOOK COMPLETE")
    print(f"[PLAYBOOK]    IP:      {alert.source_ip}")
    print(f"[PLAYBOOK]    Action:  {action}")
    print(f"[PLAYBOOK]    Score:   {intel['abuse_score']}/100")
    print(f"[PLAYBOOK]    Verdict: {intel.get('verdict', 'Unknown')}")
    print(f"[PLAYBOOK] {'='*45}\n")

    return {
        'action': action,
        'intel': intel
    }


def run_credential_stuffing_playbook(alert):
    """
    Playbook for CREDENTIAL_STUFFING.
    Someone failed many times then got in!
    This is more serious — CRITICAL severity.
    """
    print(f"\n[PLAYBOOK] Running CREDENTIAL_STUFFING playbook")
    print(f"[PLAYBOOK] ⚠️  Someone may have broken in!")

    # Check intel
    intel = check_ip_reputation(alert.source_ip)

    # Block immediately — no questions asked
    blocked = block_ip_firewall(alert.source_ip)
    action = "BLOCKED" if blocked else "ALERTED_ONLY"

    # Alert with CRITICAL urgency
    send_slack_alert(alert, intel, action)

    # Save to database
    save_incident(alert, action, intel)
    if blocked:
        save_blocked_ip(alert.source_ip, alert.threat_type, intel)

    print(f"[PLAYBOOK] ✅ Credential stuffing playbook complete\n")

    return {'action': action, 'intel': intel}


# ── Map threat types to playbooks ──
PLAYBOOKS = {
    'BRUTE_FORCE':          run_brute_force_playbook,
    'CREDENTIAL_STUFFING':  run_credential_stuffing_playbook,
}


def dispatch(alert):
    """
    Main entry point.
    Receives alert → finds correct playbook → runs it.
    Prevents duplicate processing of same IP.
    """
    # Create unique key for this alert
    alert_key = f"{alert.threat_type}_{alert.source_ip}"

    # Skip if already processed
    if alert_key in processed_alerts:
        print(f"[PLAYBOOK] Already processed {alert_key} — skipping")
        return None

    # Mark as processed
    processed_alerts.add(alert_key)

    # Find and run the playbook
    playbook = PLAYBOOKS.get(alert.threat_type)

    if playbook:
        return playbook(alert)
    else:
        print(f"[PLAYBOOK] ⚠️  No playbook for {alert.threat_type}")
        return None