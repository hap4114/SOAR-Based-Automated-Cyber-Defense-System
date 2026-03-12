// frontend/src/useWebSocket.js
// Hook that connects to FastAPI WebSocket
// Gives us real-time attack alerts instantly

import { useState, useEffect, useRef } from 'react';

export function useWebSocket() {
    const [liveAlerts, setLiveAlerts] = useState([]);
    const [connected, setConnected] = useState(false);
    const ws = useRef(null);

    useEffect(() => {
        function connect() {
            console.log('[WS] Connecting to SOAR backend...');
            ws.current = new WebSocket('ws://localhost:8000/ws');

            ws.current.onopen = () => {
                setConnected(true);
                console.log('[WS] Connected!');
            };

            ws.current.onmessage = (e) => {
                const msg = JSON.parse(e.data);

                if (msg.type === 'NEW_ALERT') {
                    // Add new alert to TOP of list
                    setLiveAlerts(prev =>
                        [msg.alert, ...prev].slice(0, 50)
                    );
                }
            };

            ws.current.onclose = () => {
                setConnected(false);
                console.log('[WS] Disconnected — retrying in 3s...');
                // Auto reconnect after 3 seconds
                setTimeout(connect, 3000);
            };

            ws.current.onerror = (e) => {
                console.log('[WS] Error:', e);
            };
        }

        connect();

        // Cleanup on unmount
        return () => {
            if (ws.current) ws.current.close();
        };
    }, []);

    return { liveAlerts, connected };
}