"use client";

import { useEffect, useState } from "react";
import {
  Zap,
  BarChart3,
  AlertTriangle,
  Wind,
  RefreshCcw
} from "lucide-react";
import StatsCard from "@/components/StatsCard";
import { ProductionLineChart, PlantBarChart } from "@/components/EnergyCharts";
import { energyApi } from "@/lib/api";

export default function DashboardPage() {
  const [latestData, setLatestData] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [summary, setSummary] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [latest, anomal, summ] = await Promise.all([
        energyApi.getLatest(),
        energyApi.getAnomalies(),
        energyApi.getSummary()
      ]);
      setLatestData(latest);
      setAnomalies(anomal);
      setSummary(summ);
    } catch (err) {
      console.error("Failed to load dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Auto-refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const totalOutput = latestData.reduce((acc, curr) => acc + curr.power_output, 0).toFixed(1);
  const avgEfficiency = (summary.reduce((acc, curr) => acc + curr.efficiency, 0) / (summary.length || 1)).toFixed(1);

  return (
    <div className="flex-col gap-8 p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Plant Operations</h1>
          <p className="text-muted">Real-time performance metrics across all renewable assets</p>
        </div>
        <button
          onClick={loadData}
          className={`flex items-center gap-2 p-3 bg-secondary rounded-xl hover:bg-muted transition-colors ${loading ? 'opacity-50' : ''}`}
          disabled={loading}
        >
          <RefreshCcw size={18} className={loading ? 'animate-spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="grid grid-cols-4 mb-8">
        <StatsCard
          title="Total Production"
          value={`${totalOutput} kWh`}
          icon={Zap}
          trend="+12.5%"
        />
        <StatsCard
          title="Avg Efficiency"
          value={`${avgEfficiency}%`}
          icon={BarChart3}
          trend="+2.1%"
          color="#22c55e"
        />
        <StatsCard
          title="Active Plants"
          value={summary.length}
          icon={Wind}
          color="#a855f7"
        />
        <StatsCard
          title="Recent Anomalies"
          value={anomalies.length}
          icon={AlertTriangle}
          trend={anomalies.length > 0 ? "Critical" : "None"}
          color={anomalies.length > 0 ? "#ef4444" : "#22c55e"}
        />
      </div>

      <div className="grid grid-cols-2">
        <ProductionLineChart data={latestData} />
        <PlantBarChart data={summary} />
      </div>

      {anomalies.length > 0 && (
        <div className="mt-8 bg-destructive/10 border-destructive border p-6 rounded-xl">
          <div className="flex items-center gap-2 text-destructive font-bold mb-4">
            <AlertTriangle size={20} />
            <h2>Active Alerts</h2>
          </div>
          <div className="flex flex-col gap-2">
            {anomalies.map((a, i) => (
              <div key={i} className="flex justify-between items-center p-3 bg-card/50 rounded-lg">
                <span>{a.plant_name} — High temperature detected: {a.temperature}°C</span>
                <span className="text-sm text-muted">{new Date(a.timestamp).toLocaleTimeString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
