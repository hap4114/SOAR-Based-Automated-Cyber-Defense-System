// frontend/src/components/AttackChart.jsx
// Bar chart showing attack frequency by type

import {
    BarChart, Bar, XAxis, YAxis,
    Tooltip, ResponsiveContainer, Cell
} from 'recharts';

export default function AttackChart({ incidents }) {
    // Count incidents by threat type
    const counts = incidents.reduce((acc, inc) => {
        acc[inc.threat_type] = (acc[inc.threat_type] || 0) + 1;
        return acc;
    }, {});

    const data = Object.entries(counts).map(([type, count]) => ({
        name: type.replace('_', ' '),
        count
    }));

    const COLORS = ['#ff6b35', '#e84393', '#7b2d8b', '#00b4d8', '#06d6a0'];

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
                ATTACK FREQUENCY BY TYPE
            </div>

            {data.length === 0 ? (
                <div style={{
                    color: '#333',
                    fontSize: 13,
                    textAlign: 'center',
                    padding: 40
                }}>
                    No data yet
                </div>
            ) : (
                <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={data}>
                        <XAxis
                            dataKey="name"
                            tick={{ fill: '#555', fontSize: 11 }}
                            axisLine={{ stroke: '#1a1a2e' }}
                        />
                        <YAxis
                            tick={{ fill: '#555', fontSize: 11 }}
                            axisLine={{ stroke: '#1a1a2e' }}
                        />
                        <Tooltip
                            contentStyle={{
                                background: '#0d0d1a',
                                border: '1px solid #1a1a2e',
                                borderRadius: 8,
                                color: '#fff'
                            }}
                        />
                        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                            {data.map((_, i) => (
                                <Cell
                                    key={i}
                                    fill={COLORS[i % COLORS.length]}
                                />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            )}
        </div>
    );
}