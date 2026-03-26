/**
 * API Client for EnergyOps Backend
 */

const API_BASE = "/api/v1";

export async function fetcher(endpoint: string, options?: RequestInit) {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (!res.ok) {
        throw new Error(`API Error: ${res.statusText}`);
    }
    return res.json();
}

export const energyApi = {
    getLatest: () => fetcher("/energy/latest"),
    getAnomalies: () => fetcher("/energy/anomalies"),
    getSummary: () => fetcher("/energy/summary"),
    getTrends: () => fetcher("/energy/trends"),
};

export const ragApi = {
    index: () => fetcher("/rag/index", { method: "POST" }),
    ask: (question: string) =>
        fetcher("/rag/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        }),
};

export const monitoringApi = {
    getMetrics: async () => {
        const res = await fetch("/metrics");
        if (!res.ok) throw new Error("Failed to fetch metrics");
        return res.text();
    },
};
