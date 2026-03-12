// frontend/src/App.jsx
import { useState, useEffect } from 'react';
import { getStats, getIncidents, getBlockedIPs, resetData } from './api';
import { useWebSocket } from './useWebSocket';
import StatsBar from './components/StatsBar';
import ThreatFeed from './components/ThreatFeed';
import AttackChart from './components/AttackChart';
import BlockedIPs from './components/BlockedIPs';

export default function App() {
  const [stats, setStats] = useState({});
  const [incidents, setIncidents] = useState([]);
  const [blockedIPs, setBlockedIPs] = useState([]);
  const [loading, setLoading] = useState(true);
  const { liveAlerts, connected } = useWebSocket();

  // Load data on first render
  useEffect(() => {
    loadAllData();
  }, []);

  // Refresh stats when new live alert arrives
  useEffect(() => {
    if (liveAlerts.length > 0) {
      loadAllData();
    }
  }, [liveAlerts]);

  async function loadAllData() {
    try {
      const [s, i, b] = await Promise.all([
        getStats(),
        getIncidents(),
        getBlockedIPs()
      ]);
      setStats(s);
      setIncidents(i);
      setBlockedIPs(b);
    } catch (e) {
      console.error('Failed to load data:', e);
    } finally {
      setLoading(false);
    }
  }

  async function handleReset() {
    if (window.confirm('Clear all data? This cannot be undone.')) {
      await resetData();
      setStats({});
      setIncidents([]);
      setBlockedIPs([]);
    }
  }

  // Combine live alerts with database incidents
  const allAlerts = [
    ...liveAlerts,
    ...incidents.map(i => ({
      ...i,
      source_ip: i.source_ip,
      threat_type: i.threat_type,
      severity: i.severity,
      details: i.details,
      action: i.action_taken,
      timestamp: i.timestamp
    }))
  ].slice(0, 50);

  return (
    <div style={{
      background: '#080810',
      minHeight: '100vh',
      color: '#ddd',
      fontFamily: "'Courier New', monospace",
      padding: 20
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 24,
        paddingBottom: 16,
        borderBottom: '1px solid #1a1a2e'
      }}>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: 22,
            fontWeight: 900,
            background: 'linear-gradient(90deg, #ff6b35, #e84393, #00b4d8)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            🛡️ SOAR Security Dashboard
          </h1>
          <div style={{ fontSize: 11, color: '#444', marginTop: 4 }}>
            Automated Threat Detection & Response System
          </div>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 16
        }}>
          {/* Live indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 11
          }}>
            <div style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: connected ? '#00ff88' : '#ff4444',
              boxShadow: connected
                ? '0 0 8px #00ff88'
                : '0 0 8px #ff4444'
            }} />
            <span style={{
              color: connected ? '#00ff88' : '#ff4444'
            }}>
              {connected ? 'LIVE' : 'DISCONNECTED'}
            </span>
          </div>

          {/* Reset button */}
          <button
            onClick={handleReset}
            style={{
              background: 'transparent',
              border: '1px solid #1a1a2e',
              color: '#444',
              padding: '6px 14px',
              borderRadius: 6,
              cursor: 'pointer',
              fontSize: 11,
              fontFamily: 'monospace'
            }}
          >
            Reset Data
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{
          textAlign: 'center',
          color: '#444',
          marginTop: 100,
          fontSize: 14
        }}>
          Connecting to SOAR backend...
        </div>
      ) : (
        <>
          {/* Stats Row */}
          <StatsBar
            stats={stats}
            liveCount={liveAlerts.length}
          />

          {/* Live Threat Feed — full width */}
          <div style={{ marginBottom: 20 }}>
            <ThreatFeed alerts={allAlerts} />
          </div>

          {/* Bottom Row — Chart + Blocked IPs */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 20
          }}>
            <AttackChart incidents={incidents} />
            <BlockedIPs blockedIPs={blockedIPs} />
          </div>
        </>
      )}
    </div>
  );
}