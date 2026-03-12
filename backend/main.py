# backend/main.py

import asyncio
import threading
import time
import os
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import our modules
from backend.database import init_database, get_all_incidents, get_stats
from backend.log_monitor import start_monitoring
from backend.threat_detector import ThreatDetector
from backend.playbook_engine import dispatch

load_dotenv()

# ─────────────────────────────────────
# App Setup
# ─────────────────────────────────────

app = FastAPI(
    title="SOAR System API",
    description="Security Orchestration Automation and Response",
    version="1.0.0"
)

# Allow React frontend to connect
# Without this browser blocks the connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─────────────────────────────────────
# WebSocket Manager
# Keeps track of all connected dashboards
# ─────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        # List of all connected dashboard clients
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Dashboard connected! Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[WS] Dashboard disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to ALL connected dashboards."""
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()
detector = ThreatDetector()

# Store reference to event loop
main_loop = None

# ─────────────────────────────────────
# Event Handler
# Called by log monitor for each event
# ─────────────────────────────────────

def on_new_event(event):
    """
    Called every time log monitor finds a new event.
    Runs in background thread.
    """
    # Run threat detection
    alert = detector.analyze(event)

    if alert:
        print(f"\n[MAIN] 🚨 Alert detected — running playbook...")
        result = dispatch(alert)

        if result:
            # Broadcast to all connected dashboards
            message = {
                'type': 'NEW_ALERT',
                'alert': {
                    'threat_type':  alert.threat_type,
                    'severity':     alert.severity,
                    'source_ip':    alert.source_ip,
                    'details':      alert.details,
                    'timestamp':    alert.timestamp,
                    'action':       result.get('action', 'UNKNOWN'),
                    'abuse_score':  result.get('intel', {}).get('abuse_score', -1),
                    'verdict':      result.get('intel', {}).get('verdict', 'Unknown'),
                    'country':      result.get('intel', {}).get('country', 'Unknown'),
                }
            }

            # Send to dashboard via WebSocket
            if main_loop and main_loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    manager.broadcast(message),
                    main_loop
                )

# ─────────────────────────────────────
# Startup Event
# Runs when server starts
# ─────────────────────────────────────

@app.on_event("startup")
async def startup():
    global main_loop
    main_loop = asyncio.get_event_loop()

    # Initialize database
    init_database()

    # Start log monitoring in background thread
    log_path = os.getenv('LOG_PATH', './logs/simulated_auth.log')
    start_monitoring(log_path, on_new_event)

    print("\n" + "="*50)
    print("🛡️  SOAR SYSTEM ONLINE")
    print("="*50)
    print(f"📁 Monitoring: {log_path}")
    print(f"🌐 API Docs:   http://localhost:8000/docs")
    print(f"📊 Dashboard:  http://localhost:3000")
    print("="*50 + "\n")


# ─────────────────────────────────────
# WebSocket Endpoint
# Dashboard connects here for live updates
# ─────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ─────────────────────────────────────
# REST API Endpoints
# Dashboard calls these for data
# ─────────────────────────────────────

@app.get("/")
def root():
    """Health check — is server running?"""
    return {
        "status": "online",
        "system": "SOAR",
        "version": "1.0.0"
    }


@app.get("/api/incidents")
def get_incidents():
    """
    Get all incidents from database.
    Dashboard calls this on first load.
    """
    incidents = get_all_incidents()
    return {
        "count": len(incidents),
        "incidents": incidents
    }


@app.get("/api/stats")
def get_statistics():
    """
    Get summary statistics.
    Used by dashboard stats bar.
    """
    return get_stats()


@app.get("/api/blocked-ips")
def get_blocked_ips():
    """Get list of all blocked IPs."""
    import sqlite3
    conn = sqlite3.connect(os.getenv('DB_PATH', './soar.db'))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        'SELECT * FROM blocked_ips ORDER BY blocked_at DESC'
    ).fetchall()
    conn.close()
    return {
        "count": len(rows),
        "blocked_ips": [dict(row) for row in rows]
    }


@app.get("/api/recent")
def get_recent_incidents():
    """Get last 10 incidents — for live feed."""
    import sqlite3
    conn = sqlite3.connect(os.getenv('DB_PATH', './soar.db'))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        'SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 10'
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.delete("/api/reset")
def reset_database():
    """
    Clear all data — useful for testing.
    WARNING: deletes everything!
    """
    import sqlite3
    conn = sqlite3.connect(os.getenv('DB_PATH', './soar.db'))
    conn.execute('DELETE FROM incidents')
    conn.execute('DELETE FROM blocked_ips')
    conn.commit()
    conn.close()

    # Clear in-memory tracking
    from response_actions import blocked_ips
    from playbook_engine import processed_alerts
    blocked_ips.clear()
    processed_alerts.clear()

    return {"status": "reset complete"}