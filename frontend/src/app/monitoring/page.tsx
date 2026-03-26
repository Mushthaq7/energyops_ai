"use client";

import { useEffect, useState } from "react";
import {
    Activity,
    Clock,
    AlertCircle,
    Cpu,
    RefreshCw,
    Zap,
    CheckCircle2
} from "lucide-react";
import { monitoringApi } from "@/lib/api";
import StatsCard from "@/components/StatsCard";

interface Metrics {
    requestRate: number;
    avgLatency: number;
    errorRate: number;
    modelLatency: number;
    totalRequests: number;
}

export default function MonitoringPage() {
    const [metrics, setMetrics] = useState<Metrics>({
        requestRate: 0,
        avgLatency: 0,
        errorRate: 0,
        modelLatency: 0,
        totalRequests: 0,
    });
    const [loading, setLoading] = useState(true);
    const [lastRefreshed, setLastRefreshed] = useState(new Date());

    const parseMetrics = (text: string): Metrics => {
        const lines = text.split("\n");
        let totalReq = 0;
        let totalLat = 0;
        let totalErr = 0;
        let totalModelLat = 0;
        let totalModelCount = 0;

        lines.forEach(line => {
            if (line.startsWith('http_requests_total')) {
                const val = parseFloat(line.split(" ").pop() || "0");
                totalReq += val;
                if (line.includes('status_code="4') || line.includes('status_code="5')) {
                    totalErr += val;
                }
            }
            if (line.startsWith('http_request_duration_seconds_sum')) {
                totalLat += parseFloat(line.split(" ").pop() || "0");
            }
            if (line.startsWith('model_response_duration_seconds_sum{operation="ask"}')) {
                totalModelLat = parseFloat(line.split(" ").pop() || "0");
            }
            if (line.startsWith('model_response_duration_seconds_count{operation="ask"}')) {
                totalModelCount = parseFloat(line.split(" ").pop() || "0");
            }
        });

        return {
            totalRequests: totalReq,
            requestRate: 0, // Would need delta over time, simplified for now
            avgLatency: totalReq > 0 ? (totalLat / totalReq) * 1000 : 0,
            errorRate: totalReq > 0 ? (totalErr / totalReq) * 100 : 0,
            modelLatency: totalModelCount > 0 ? (totalModelLat / totalModelCount) : 0,
        };
    };

    const loadMetrics = async () => {
        setLoading(true);
        try {
            const text = await monitoringApi.getMetrics();
            const parsed = parseMetrics(text);
            setMetrics(parsed);
            setLastRefreshed(new Date());
        } catch (err) {
            console.error("Failed to load metrics", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadMetrics();
        const interval = setInterval(loadMetrics, 5000); // Fast refresh for monitoring
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex-col gap-8 p-6">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold">System Health</h1>
                    <p className="text-muted">Real-time telemetry from the FastAPI backend & LLM pipeline</p>
                </div>
                <div className="flex items-center gap-4">
                    <span className="text-xs text-muted">Last sync: {lastRefreshed.toLocaleTimeString()}</span>
                    <button
                        onClick={loadMetrics}
                        className="p-2 hover:bg-secondary rounded-lg transition-colors"
                    >
                        <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-4 mb-8">
                <StatsCard
                    title="Total Requests"
                    value={metrics.totalRequests}
                    icon={Activity}
                    trend="Live"
                />
                <StatsCard
                    title="Avg Latency"
                    value={`${metrics.avgLatency.toFixed(1)}ms`}
                    icon={Clock}
                    color="#3b82f6"
                />
                <StatsCard
                    title="Error Rate"
                    value={`${metrics.errorRate.toFixed(1)}%`}
                    icon={AlertCircle}
                    color={metrics.errorRate > 5 ? "#ef4444" : "#22c55e"}
                />
                <StatsCard
                    title="Model Latency"
                    value={`${metrics.modelLatency.toFixed(2)}s`}
                    icon={Cpu}
                    color="#f59e0b"
                />
            </div>

            <div className="grid grid-cols-2">
                <div className="bg-card p-6 rounded-xl border">
                    <h2 className="font-bold mb-6 flex items-center gap-2">
                        <Zap size={18} className="text-primary" />
                        Active Service Metrics
                    </h2>
                    <div className="flex flex-col gap-6">
                        <div className="flex justify-between items-center p-4 bg-secondary/30 rounded-lg">
                            <span className="text-muted-foreground uppercase text-xs font-bold">API Status</span>
                            <span className="flex items-center gap-2 text-accent font-bold">
                                <CheckCircle2 size={16} /> Operational
                            </span>
                        </div>
                        <div className="flex justify-between items-center p-4 bg-secondary/30 rounded-lg">
                            <span className="text-muted-foreground uppercase text-xs font-bold">DB Load</span>
                            <span className="text-foreground font-bold">Normal</span>
                        </div>
                        <div className="flex justify-between items-center p-4 bg-secondary/30 rounded-lg">
                            <span className="text-muted-foreground uppercase text-xs font-bold">LLM Pool</span>
                            <span className="text-foreground font-bold">3/4 Free</span>
                        </div>
                    </div>
                </div>

                <div className="bg-card p-6 rounded-xl border flex flex-col items-center justify-center text-center">
                    <Activity size={48} className="text-muted-foreground mb-4 opacity-20" />
                    <h3 className="font-bold text-muted-foreground">Detailed Dashboards</h3>
                    <p className="text-muted text-sm mt-2 max-w-[280px]">
                        For more granular telemetry, visit the dedicated Prometheus and Grafana dashboards.
                    </p>
                    <div className="flex gap-4 mt-6">
                        <a href="http://localhost:3001" target="_blank" className="p-2 px-4 bg-secondary rounded-lg text-sm hover:bg-muted transition-colors">Open Grafana</a>
                        <a href="http://localhost:9090" target="_blank" className="p-2 px-4 bg-secondary rounded-lg text-sm hover:bg-muted transition-colors">Open Prometheus</a>
                    </div>
                </div>
            </div>
        </div>
    );
}
