# backend/database.py

import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv('DB_PATH', './soar.db')


def init_database():
    """
    Creates database tables if they don't exist.
    Run this once when program starts.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Main incidents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            threat_type     TEXT,
            severity        TEXT,
            source_ip       TEXT,
            details         TEXT,
            action_taken    TEXT,
            abuse_score     INTEGER,
            verdict         TEXT,
            country         TEXT,
            sources_found   INTEGER,
            timestamp       TEXT
        )
    ''')

    # Blocked IPs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_ips (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            ip              TEXT UNIQUE,
            reason          TEXT,
            blocked_at      TEXT,
            abuse_score     INTEGER,
            country         TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] ✅ Database initialized")


def save_incident(alert, action_taken, threat_intel=None):
    """Save a detected incident to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO incidents
        (threat_type, severity, source_ip, details,
         action_taken, abuse_score, verdict, country,
         sources_found, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        alert.threat_type,
        alert.severity,
        alert.source_ip,
        alert.details,
        action_taken,
        threat_intel.get('abuse_score', -1) if threat_intel else -1,
        threat_intel.get('verdict', 'Unknown') if threat_intel else 'Unknown',
        threat_intel.get('country', 'Unknown') if threat_intel else 'Unknown',
        threat_intel.get('sources_found', 0) if threat_intel else 0,
        alert.timestamp
    ))

    conn.commit()
    conn.close()
    print(f"[DB] ✅ Incident saved to database")


def save_blocked_ip(ip, reason, threat_intel=None):
    """Save a blocked IP to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR IGNORE INTO blocked_ips
            (ip, reason, blocked_at, abuse_score, country)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            ip,
            reason,
            __import__('datetime').datetime.now().isoformat(),
            threat_intel.get('abuse_score', -1) if threat_intel else -1,
            threat_intel.get('country', 'Unknown') if threat_intel else 'Unknown'
        ))
        conn.commit()
        print(f"[DB] ✅ {ip} saved to blocked IPs")
    except Exception as e:
        print(f"[DB] ❌ Error saving blocked IP: {e}")
    finally:
        conn.close()


def get_all_incidents():
    """Get all incidents — used by dashboard."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        'SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 100'
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats():
    """Get summary stats — used by dashboard."""
    conn = sqlite3.connect(DB_PATH)

    total = conn.execute(
        'SELECT COUNT(*) FROM incidents'
    ).fetchone()[0]

    blocked = conn.execute(
        "SELECT COUNT(*) FROM incidents WHERE action_taken='BLOCKED'"
    ).fetchone()[0]

    high_severity = conn.execute(
        "SELECT COUNT(*) FROM incidents WHERE severity='HIGH' OR severity='CRITICAL'"
    ).fetchone()[0]

    conn.close()

    return {
        'total_incidents': total,
        'ips_blocked': blocked,
        'high_severity': high_severity
    }