# 🛡️ SOAR-Based Automated Cyber Defense System

A Security Orchestration, Automation, and Response (SOAR) system 
that automatically detects and responds to cyber threats in real-time.
No human intervention required.

Built as a portfolio project for MS Cybersecurity applications.

---

## 📋 Table of Contents
- [What It Does](#what-it-does)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Firewall Setup](#firewall-setup)
- [API Endpoints](#api-endpoints)
- [How Detection Works](#how-detection-works)
- [Threat Intelligence Sources](#threat-intelligence-sources)

---

## What It Does
```
Attacker tries 5+ wrong passwords
         ↓
Log monitor detects the attempts
         ↓
Threat detector fires BRUTE_FORCE alert
         ↓
Checks 4 threat intelligence sources
         ↓
Automatically blocks attacker IP
         ↓
Sends Slack alert to your phone
         ↓
Saves incident to database
         ↓
Dashboard updates in real time
```

Total time from attack to block: ~1 second ⚡

---

## Architecture
```
┌─────────────────────────────────────────┐
│           SOAR PIPELINE                 │
│                                         │
│  Log File                               │
│     ↓                                   │
│  log_monitor.py   (watches log file)    │
│     ↓                                   │
│  threat_detector.py  (detection rules)  │
│     ↓                                   │
│  threat_intel.py  (4 sources checked)   │
│     ↓                                   │
│  playbook_engine.py  (orchestration)    │
│     ↓                                   │
│  response_actions.py (block+alert+log)  │
│     ↓                                   │
│  FastAPI + WebSocket                    │
│     ↓                                   │
│  React Dashboard                        │
└─────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| Database | SQLite |
| Frontend | React, Recharts |
| Security Tools | iptables, netsh |
| Threat Intel | AbuseIPDB, ipsum, Emerging Threats, Firehol |
| Alerting | Slack Webhooks |
| Real-time | WebSockets |

---

## Project Structure
```
soar-system/
├── backend/
│   ├── main.py              # FastAPI server + WebSocket
│   ├── log_monitor.py       # Real-time log file watcher
│   ├── threat_detector.py   # Detection rules engine
│   ├── playbook_engine.py   # Orchestration logic
│   ├── response_actions.py  # Block IP, send alerts
│   ├── threat_intel.py      # Multi-source threat intel
│   ├── database.py          # SQLite operations
│   └── data/
│       ├── ipsum.txt           # ipsum threat list
│       ├── emerging_threats.txt # Emerging Threats list
│       └── firehol.txt         # Firehol Level 1 list
├── frontend/
│   └── src/                 # React dashboard
├── logs/
│   └── simulated_auth.log   # Test log file
├── tools/
│   ├── simulate_attack.py   # Attack simulator for testing
│   └── update_dataset.py    # Updates local threat datasets
├── .env                     # Secret keys (never commit!)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/soar-system.git
cd soar-system
```

### 2. Create virtual environment
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your keys
ABUSEIPDB_API_KEY=your_key_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
DB_PATH=./soar.db
LOG_PATH=./logs/simulated_auth.log
```

### 5. Download threat intelligence datasets
```bash
python tools/update_dataset.py
```

### 6. Start the backend server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 7. Start the frontend dashboard
```bash
cd frontend
npm install
npm start
```

### 8. Simulate an attack (for testing)
```bash
# Open new terminal
python tools/simulate_attack.py
```

---

## 🔒 Firewall Setup

The system supports real firewall blocking AND demo mode.

### Current Mode: Demo (Simulated Block)
By default the system runs in demo mode.
The block is simulated and logged — 
no actual firewall rules are changed.
This is safe for testing on your personal laptop.
```python
# In backend/response_actions.py
# Current behavior — safe for demo:
if not success:
    print("Simulating block for demo")
    success = True  # Simulates the block
```

---

### Option A: Enable REAL Firewall Blocking on Windows

⚠️ WARNING: This will actually block IPs on your machine.
Only do this on a dedicated test machine or server.

**Step 1:** Open PowerShell as Administrator
```
Search "PowerShell" → Right click → Run as Administrator
```

**Step 2:** Run the server as admin
```bash
cd soar-system\backend
..\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Step 3:** Enable real blocking in response_actions.py
```python
# Find this section in response_actions.py
# REMOVE the simulated block lines:

if not success:
    print(f"[RESPONSE] Simulating block for {ip}")
    success = True  # ← DELETE THIS LINE
```

**Step 4:** To unblock an IP manually
```bash
# In PowerShell as Administrator:
netsh advfirewall firewall delete rule name="SOAR_BLOCK_<IP_ADDRESS>"

# Example:
netsh advfirewall firewall delete rule name="SOAR_BLOCK_45.33.32.156"
```

**Step 5:** To see all SOAR block rules
```bash
netsh advfirewall firewall show rule name=all | findstr "SOAR"
```

**Step 6:** To remove ALL SOAR rules at once
```bash
# PowerShell as Admin:
Get-NetFirewallRule | Where-Object {$_.Name -like "SOAR_BLOCK_*"} | Remove-NetFirewallRule
```

---

### Option B: Enable REAL Firewall Blocking on Linux

This is the recommended production setup.

**Step 1:** Run on a Linux server (Ubuntu recommended)

**Step 2:** Make sure iptables is installed
```bash
sudo apt-get install iptables
```

**Step 3:** Run server with sudo
```bash
sudo uvicorn main:app --port 8000
```

**Step 4:** SOAR will automatically run:
```bash
sudo iptables -A INPUT -s <attacker_ip> -j DROP
```

**Step 5:** To see all blocked IPs
```bash
sudo iptables -L INPUT -n
```

**Step 6:** To unblock a specific IP
```bash
sudo iptables -D INPUT -s <IP_ADDRESS> -j DROP
```

**Step 7:** To remove ALL SOAR blocks
```bash
sudo iptables -F INPUT
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/stats` | Summary statistics |
| GET | `/api/incidents` | All incidents |
| GET | `/api/blocked-ips` | All blocked IPs |
| GET | `/api/recent` | Last 10 incidents |
| DELETE | `/api/reset` | Clear all data |
| WS | `/ws` | WebSocket live feed |

Full interactive docs available at:
```
http://localhost:8000/docs
```

---

## How Detection Works

### Brute Force Detection
```
Rule: Same IP fails login 5+ times in 60 seconds
Severity: HIGH
Action: Block IP + Slack alert + Log incident
```

### Credential Stuffing Detection
```
Rule: Successful login after 3+ failures from same IP
Severity: CRITICAL
Action: Block IP + Slack alert + Log incident
```

---

## Threat Intelligence Sources

The system checks ALL 4 sources and combines scores:

| Source | Type | Updates |
|--------|------|---------|
| AbuseIPDB | Live API | Real-time |
| ipsum | Local dataset | Daily |
| Emerging Threats | Local dataset | Daily |
| Firehol Level 1 | Local dataset | Daily |

### Scoring System
```
1 source flags IP  → base score
2 sources flag IP  → base score + 10 bonus
3 sources flag IP  → base score + 20 bonus
4 sources flag IP  → base score + 30 bonus (DANGEROUS)
```

### Fallback System
```
AbuseIPDB works    → use live score ✅
AbuseIPDB exhausted → use local datasets ✅
Not in any dataset  → block anyway (behavior = enough proof) ✅
```

---

## Resume Description
```
SOAR-Based Automated Cyber Defense System
Technologies: Python, FastAPI, React, SQLite, 
              Linux Security Tools, Threat Intelligence APIs

- Developed a Security Orchestration, Automation and Response 
  (SOAR) system to automatically detect and mitigate cyber threats

- Implemented real-time log monitoring and rule-based detection 
  for brute force attacks and credential stuffing

- Integrated 4 threat intelligence sources (AbuseIPDB, ipsum, 
  Emerging Threats, Firehol) with intelligent fallback system

- Designed automated response pipeline: IP blocking, Slack 
  alerting, and incident logging — response time under 1 second

- Built REST API with FastAPI and real-time WebSocket updates 
  for live SOC dashboard visualization
```

---

## Future Improvements
- [ ] Machine learning based anomaly detection
- [ ] Port scan detection
- [ ] DDoS detection
- [ ] Email alerting
- [ ] Docker deployment
- [ ] Cloud deployment (AWS/Azure)
- [ ] MITRE ATT&CK framework mapping

---

## License
MIT License — free to use and modify

