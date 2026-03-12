// frontend/src/components/ThreatFeed.jsx
// Live scrolling list of attacks

const SEVERITY_COLORS = {
    LOW: '#4caf50',
    MEDIUM: '#ff9800',
    HIGH: '#ff4444',
    CRITICAL: '#9c27b0'
};

export default function ThreatFeed({ alerts }) {
    return (
        <div style={{
            background: '#0d0d1a',
            border: '1px solid #1a1a2e',
            borderRadius: 10,
            padding: 20,
            height: 340,
            overflow: 'hidden'
        }}>
            {/* Header */}
            <div style={{
                fontSize: 10,
                letterSpacing: 3,
                color: '#444',
                marginBottom: 16,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <span>LIVE THREAT FEED</span>
                <span style={{ color: '#333' }}>
                    {alerts.length} events
                </span>
            </div>

            {/* Column Headers */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: '80px 130px 160px 1fr 100px',
                gap: 8,
                fontSize: 10,
                color: '#333',
                letterSpacing: 1,
                marginBottom: 8,
                paddingBottom: 8,
                borderBottom: '1px solid #111'
            }}>
                <span>SEVERITY</span>
                <span>IP ADDRESS</span>
                <span>THREAT TYPE</span>
                <span>DETAILS</span>
                <span>ACTION</span>
            </div>

            {/* Alert Rows */}
            <div style={{ overflowY: 'auto', height: 230 }}>
                {alerts.length === 0 ? (
                    <div style={{
                        color: '#333',
                        fontSize: 13,
                        textAlign: 'center',
                        marginTop: 60
                    }}>
                        🟢 No threats detected — system monitoring...
                    </div>
                ) : (
                    alerts.map((alert, i) => (
                        <div key={i} style={{
                            display: 'grid',
                            gridTemplateColumns: '80px 130px 160px 1fr 100px',
                            gap: 8,
                            padding: '8px 0',
                            borderBottom: '1px solid #0a0a14',
                            fontSize: 12,
                            alignItems: 'center',
                            // Flash animation for newest alert
                            background: i === 0 ? '#ffffff08' : 'transparent'
                        }}>
                            {/* Severity Badge */}
                            <span style={{
                                color: SEVERITY_COLORS[alert.severity] || '#888',
                                background: (SEVERITY_COLORS[alert.severity] || '#888') + '22',
                                padding: '2px 8px',
                                borderRadius: 4,
                                fontSize: 10,
                                fontWeight: 700,
                                textAlign: 'center'
                            }}>
                                {alert.severity}
                            </span>

                            {/* IP */}
                            <span style={{ color: '#ff6b35', fontFamily: 'monospace' }}>
                                {alert.source_ip}
                            </span>

                            {/* Threat Type */}
                            <span style={{ color: '#e84393', fontSize: 11 }}>
                                {alert.threat_type}
                            </span>

                            {/* Details */}
                            <span style={{ color: '#555', fontSize: 11 }}>
                                {alert.details}
                            </span>

                            {/* Action */}
                            <span style={{
                                color: alert.action === 'BLOCKED' ? '#00ff88' : '#ffaa00',
                                fontSize: 10,
                                fontWeight: 700
                            }}>
                                {alert.action === 'BLOCKED' ? '🔒 BLOCKED' : '⚠️ ALERTED'}
                            </span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}