// frontend/src/api.js
// All API calls to our FastAPI backend in one place

import axios from 'axios';

const BASE = 'http://localhost:8000';

export const getStats = async () => {
    const r = await axios.get(`${BASE}/api/stats`);
    return r.data;
};

export const getIncidents = async () => {
    const r = await axios.get(`${BASE}/api/incidents`);
    return r.data.incidents;
};

export const getBlockedIPs = async () => {
    const r = await axios.get(`${BASE}/api/blocked-ips`);
    return r.data.blocked_ips;
};

export const resetData = async () => {
    const r = await axios.delete(`${BASE}/api/reset`);
    return r.data;
};