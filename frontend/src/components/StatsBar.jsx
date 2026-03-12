// frontend/src/components/StatsBar.jsx
// Shows 3 big numbers at the top of dashboard

export default function StatsBar({ stats, liveCount }) {
    const cards = [
        {
            label: 'Total Incidents',
            value: stats.total_incidents || 0,
            color: '#ff6b35',
            icon: '⚡'
        },
        {
            label: 'IPs Blocked',
            value: stats.ips_blocked || 0,
            color: '#e84393',
            icon: '🔒'
        },
        {
            label: 'High Severity',
            value: stats.high_severity || 0,
            color: '#ff4444',
            icon: '🚨'
        },
        {
            label: 'Live Alerts',
            value: liveCount || 0,
            color: '#00b4d8',
            icon: '📡'
        }
    ];

    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: 16,
            marginBottom: 24
        }}>
            {cards.map(card => (
                <div key={card.label} style={{
                    background: '#0d0d1a',
                    border: `1px solid ${card.color}44`,
                    borderRadius: 10,
                    padding: 20,
                    textAlign: 'center',
                    boxShadow: `0 0 20px ${card.color}11`
                }}>
                    <div style={{ fontSize: 24, marginBottom: 8 }}>
                        {card.icon}
                    </div>
                    <div style={{
                        fontSize: 36,
                        fontWeight: 900,
                        color: card.color,
                        lineHeight: 1
                    }}>
                        {card.value}
                    </div>
                    <div style={{
                        fontSize: 11,
                        color: '#555',
                        marginTop: 6,
                        letterSpacing: 1
                    }}>
                        {card.label.toUpperCase()}
                    </div>
                </div>
            ))}
        </div>
    );
}