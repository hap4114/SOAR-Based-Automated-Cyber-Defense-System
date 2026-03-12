// frontend/src/components/BlockedIPs.jsx
// Table of all blocked IPs

export default function BlockedIPs({ blockedIPs }) {
    return (
        <div style={{
            background: '#0d0d1a',
            border: '1px solid #1a1a2e',
            borderRadius: 10,
            padding: 20
        }}>
            <div style={{
                fontSize: 10,
                letterSpacing: 3,
                color: '#444',
                marginBottom: 16
            }}>
                BLOCKED IP REGISTRY
            </div>

            {blockedIPs.length === 0 ? (
                <div style={{
                    color: '#333',
                    fontSize: 13,
                    textAlign: 'center',
                    padding: 20
                }}>
                    No IPs blocked yet
                </div>
            ) : (
                <table style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    fontSize: 12
                }}>
                    <thead>
                        <tr style={{
                            borderBottom: '1px solid #1a1a2e',
                            color: '#333',
                            fontSize: 10,
                            letterSpacing: 1
                        }}>
                            <th style={{ padding: '8px 0', textAlign: 'left' }}>IP ADDRESS</th>
                            <th style={{ padding: '8px 0', textAlign: 'left' }}>REASON</th>
                            <th style={{ padding: '8px 0', textAlign: 'left' }}>COUNTRY</th>
                            <th style={{ padding: '8px 0', textAlign: 'left' }}>SCORE</th>
                            <th style={{ padding: '8px 0', textAlign: 'left' }}>BLOCKED AT</th>
                        </tr>
                    </thead>
                    <tbody>
                        {blockedIPs.map((ip, i) => (
                            <tr key={i} style={{
                                borderBottom: '1px solid #0a0a14'
                            }}>
                                <td style={{
                                    padding: '10px 0',
                                    color: '#ff6b35',
                                    fontFamily: 'monospace'
                                }}>
                                    {ip.ip}
                                </td>
                                <td style={{ color: '#e84393' }}>
                                    {ip.reason}
                                </td>
                                <td style={{ color: '#888' }}>
                                    {ip.country || 'Unknown'}
                                </td>
                                <td style={{
                                    color: ip.abuse_score > 70
                                        ? '#ff4444'
                                        : ip.abuse_score > 30
                                            ? '#ff9800'
                                            : '#4caf50'
                                }}>
                                    {ip.abuse_score > 0
                                        ? `${ip.abuse_score}/100`
                                        : 'N/A'
                                    }
                                </td>
                                <td style={{ color: '#555', fontSize: 11 }}>
                                    {new Date(ip.blocked_at)
                                        .toLocaleString()}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}