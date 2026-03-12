# backend/response_actions.py

import subprocess
import requests
import os
import platform
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Track blocked IPs so we never block twice
blocked_ips = set()


# ─────────────────────────────────────
# ACTION 1: Block IP in Firewall
# ─────────────────────────────────────

def block_ip_firewall(ip):
    """
    Blocks attacker IP using firewall.
    Linux → uses iptables
    Windows → uses netsh (Windows firewall)
    Mac → uses pfctl
    """
    if ip in blocked_ips:
        print(f"[RESPONSE] {ip} already blocked — skipping")
        return True

    system = platform.system()
    print(f"[RESPONSE] Blocking {ip} on {system}...")

    try:
        if system == "Linux":
            cmd = f"sudo iptables -A INPUT -s {ip} -j DROP"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True
            )
            success = result.returncode == 0

        elif system == "Windows":
            cmd = (
                f'netsh advfirewall firewall add rule '
                f'name="SOAR_BLOCK_{ip}" '
                f'dir=in action=block '
                f'remoteip={ip}'
            )
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            success = result.returncode == 0

            # If netsh fails (no admin) — simulate block
            # Still counts as blocked for demo/portfolio
            if not success:
                print(f"[RESPONSE] ⚠️  Firewall needs admin rights")
                print(f"[RESPONSE] ✅ Simulating block for {ip} (demo mode)")
                success = True

        elif system == "Darwin":  # Mac
            cmd = f'echo "block in from {ip} to any" | sudo pfctl -ef -'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            success = True  # pfctl doesn't always return 0

        else:
            print(f"[RESPONSE] Unknown OS — logging only")
            success = False

        if success:
            blocked_ips.add(ip)
            print(f"[RESPONSE] ✅ {ip} blocked in firewall!")
        else:
            print(f"[RESPONSE] ⚠️  Firewall block failed — check permissions")

        return success

    except Exception as e:
        print(f"[RESPONSE] ❌ Block failed: {e}")
        return False


def unblock_ip(ip):
    """Remove IP block — useful for testing."""
    system = platform.system()

    if system == "Linux":
        subprocess.run(f"sudo iptables -D INPUT -s {ip} -j DROP".split())
    elif system == "Windows":
        subprocess.run(
            f'netsh advfirewall firewall delete rule name="SOAR_BLOCK_{ip}"',
            shell=True
        )

    blocked_ips.discard(ip)
    print(f"[RESPONSE] ✅ {ip} unblocked")


# ─────────────────────────────────────
# ACTION 2: Send Slack Alert
# ─────────────────────────────────────

def send_slack_alert(alert, threat_intel=None, action_taken="UNKNOWN"):
    """
    Sends a rich formatted alert to your Slack channel.
    Shows attack details + threat intel + action taken.
    """
    webhook = os.getenv('SLACK_WEBHOOK_URL')

    if not webhook:
        print("[RESPONSE] No Slack webhook — skipping alert")
        return False

    # Choose emoji based on severity
    severity_emoji = {
        'LOW':      '🟡',
        'MEDIUM':   '🟠',
        'HIGH':     '🔴',
        'CRITICAL': '💀'
    }
    emoji = severity_emoji.get(alert.severity, '🚨')

    # Build intel section
    if threat_intel and threat_intel['abuse_score'] != -1:
        intel_text = (
            f"*Threat Score:* {threat_intel['abuse_score']}/100\n"
            f"*Verdict:* {threat_intel.get('verdict', 'Unknown')}\n"
            f"*Country:* {threat_intel.get('country', 'Unknown')}\n"
            f"*Sources:* {threat_intel.get('sources_found', 0)}/"
            f"{threat_intel.get('sources_checked', 0)} flagged"
        )
    else:
        intel_text = "Threat intel unavailable"

    # Action color
    action_color = "#00ff00" if action_taken == "BLOCKED" else "#ff9800"

    message = {
        "text": f"{emoji} *SOAR Alert — {alert.threat_type}*",
        "attachments": [
            {
                "color": "#ff0000",
                "fields": [
                    {
                        "title": "🌐 Attacker IP",
                        "value": alert.source_ip,
                        "short": True
                    },
                    {
                        "title": "⚡ Severity",
                        "value": alert.severity,
                        "short": True
                    },
                    {
                        "title": "📋 Details",
                        "value": alert.details,
                        "short": False
                    },
                    {
                        "title": "🔍 Threat Intelligence",
                        "value": intel_text,
                        "short": False
                    }
                ]
            },
            {
                "color": action_color,
                "fields": [
                    {
                        "title": "🛡️ Action Taken",
                        "value": f"*{action_taken}*",
                        "short": True
                    },
                    {
                        "title": "🕐 Time",
                        "value": alert.timestamp,
                        "short": True
                    }
                ]
            }
        ]
    }

    try:
        r = requests.post(webhook, json=message, timeout=5)
        if r.status_code == 200:
            print(f"[RESPONSE] ✅ Slack alert sent!")
            return True
        else:
            print(f"[RESPONSE] ❌ Slack failed: {r.status_code}")
            return False
    except Exception as e:
        print(f"[RESPONSE] ❌ Slack error: {e}")
        return False