"use client";

import { useState, useEffect } from "react";
import { Settings, Database, Brain, Activity, CheckCircle2, XCircle } from "lucide-react";

interface ServiceStatus {
    label: string;
    url: string;
    status: "checking" | "online" | "offline";
}

export default function SettingsPage() {
    const [services, setServices] = useState<ServiceStatus[]>([
        { label: "Backend API", url: "http://localhost:8000/health", status: "checking" },
        { label: "MLflow", url: "http://localhost:5000", status: "checking" },
        { label: "Prometheus", url: "http://localhost:9090", status: "checking" },
        { label: "Grafana", url: "http://localhost:3001", status: "checking" },
    ]);

    useEffect(() => {
        services.forEach((svc, i) => {
            fetch(svc.url, { mode: "no-cors" })
                .then(() => {
                    setServices(prev =>
                        prev.map((s, idx) => idx === i ? { ...s, status: "online" } : s)
                    );
                })
                .catch(() => {
                    setServices(prev =>
                        prev.map((s, idx) => idx === i ? { ...s, status: "offline" } : s)
                    );
                });
        });
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const config = [
        { label: "Backend URL", value: "http://localhost:8000" },
        { label: "API Version", value: "/api/v1" },
        { label: "LLM Model", value: "mistralai/Mistral-7B-Instruct-v0.3" },
        { label: "Embedding Model", value: "all-MiniLM-L6-v2" },
        { label: "RAG Chunk Size", value: "500 tokens" },
        { label: "RAG Chunk Overlap", value: "50 tokens" },
        { label: "Dashboard Refresh", value: "Every 30 seconds" },
        { label: "FAISS Index", value: "data/faiss_index/ (persisted)" },
    ];

    return (
        <div className="flex-col gap-8 p-6">
            <div className="mb-6">
                <h1 className="text-3xl font-bold">Settings</h1>
                <p className="text-muted">Platform configuration and service status</p>
            </div>

            <div className="grid grid-cols-2 gap-6">
                {/* Service Status */}
                <div className="bg-card p-6 rounded-xl border">
                    <h2 className="font-bold mb-4 flex items-center gap-2">
                        <Activity size={18} className="text-primary" />
                        Service Status
                    </h2>
                    <div className="flex flex-col gap-3">
                        {services.map((svc) => (
                            <div key={svc.label} className="flex justify-between items-center p-3 bg-secondary/30 rounded-lg">
                                <div>
                                    <span className="font-medium">{svc.label}</span>
                                    <p className="text-xs text-muted-foreground mt-0.5">{svc.url}</p>
                                </div>
                                {svc.status === "checking" && (
                                    <span className="text-xs text-muted-foreground animate-pulse">Checking...</span>
                                )}
                                {svc.status === "online" && (
                                    <span className="flex items-center gap-1 text-green-500 text-sm font-medium">
                                        <CheckCircle2 size={14} /> Online
                                    </span>
                                )}
                                {svc.status === "offline" && (
                                    <span className="flex items-center gap-1 text-red-500 text-sm font-medium">
                                        <XCircle size={14} /> Offline
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                    <div className="flex gap-3 mt-4">
                        <a href="http://localhost:3001" target="_blank" className="flex-1 text-center p-2 bg-secondary rounded-lg text-sm hover:bg-muted transition-colors">
                            Open Grafana
                        </a>
                        <a href="http://localhost:9090" target="_blank" className="flex-1 text-center p-2 bg-secondary rounded-lg text-sm hover:bg-muted transition-colors">
                            Open Prometheus
                        </a>
                        <a href="http://localhost:5000" target="_blank" className="flex-1 text-center p-2 bg-secondary rounded-lg text-sm hover:bg-muted transition-colors">
                            Open MLflow
                        </a>
                    </div>
                </div>

                {/* Platform Configuration */}
                <div className="bg-card p-6 rounded-xl border">
                    <h2 className="font-bold mb-4 flex items-center gap-2">
                        <Settings size={18} className="text-primary" />
                        Platform Configuration
                    </h2>
                    <div className="flex flex-col gap-2">
                        {config.map(({ label, value }) => (
                            <div key={label} className="flex justify-between items-center p-3 bg-secondary/30 rounded-lg">
                                <span className="text-sm text-muted-foreground">{label}</span>
                                <span className="text-sm font-medium font-mono">{value}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* RAG Info */}
                <div className="bg-card p-6 rounded-xl border">
                    <h2 className="font-bold mb-4 flex items-center gap-2">
                        <Brain size={18} className="text-primary" />
                        RAG Pipeline
                    </h2>
                    <div className="flex flex-col gap-3 text-sm text-muted-foreground">
                        <p>The RAG pipeline indexes maintenance documents from <code className="bg-secondary px-1 rounded">data/documents/</code> using FAISS vector search.</p>
                        <p>The FAISS index is persisted to disk and reloaded on startup — no rebuild needed unless documents change.</p>
                        <p>To re-index after adding new documents, call:</p>
                        <pre className="bg-secondary/50 p-3 rounded-lg text-xs overflow-auto">
                            POST /api/v1/rag/index
                        </pre>
                        <p>Answers are generated via <strong>Mistral-7B-Instruct-v0.3</strong> on the HuggingFace Inference API. Set <code className="bg-secondary px-1 rounded">HF_TOKEN</code> in <code className="bg-secondary px-1 rounded">.env</code> to enable real responses.</p>
                    </div>
                </div>

                {/* Database Info */}
                <div className="bg-card p-6 rounded-xl border">
                    <h2 className="font-bold mb-4 flex items-center gap-2">
                        <Database size={18} className="text-primary" />
                        Database
                    </h2>
                    <div className="flex flex-col gap-3 text-sm text-muted-foreground">
                        <p>PostgreSQL stores all energy production records. Tables are auto-created on API startup.</p>
                        <p>To seed synthetic data for 3 plants over 30 days:</p>
                        <pre className="bg-secondary/50 p-3 rounded-lg text-xs overflow-auto">
                            python generate_data.py
                        </pre>
                        <p>Plants: <strong>SolarFarm_01</strong>, <strong>WindPark_02</strong>, <strong>HybridPlant_03</strong> — hourly readings with ~1% anomaly injection.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
