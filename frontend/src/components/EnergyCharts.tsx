"use client";

import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from "recharts";

interface ChartProps {
    data: any[];
}

export const ProductionLineChart = ({ data }: ChartProps) => {
    return (
        <div className="bg-card p-6 rounded-xl border" style={{ height: '400px' }}>
            <h3 className="font-bold mb-6">Energy Production Over Time (kWh)</h3>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                    <XAxis
                        dataKey="timestamp"
                        stroke="#a1a1aa"
                        fontSize={12}
                        tickFormatter={(val) => new Date(val).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    />
                    <YAxis stroke="#a1a1aa" fontSize={12} />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px' }}
                        itemStyle={{ color: '#3b82f6' }}
                    />
                    <Line
                        type="monotone"
                        dataKey="solar_output"
                        stroke="#f59e0b"
                        strokeWidth={3}
                        dot={false}
                        name="Solar"
                        animationDuration={1500}
                    />
                    <Line
                        type="monotone"
                        dataKey="wind_output"
                        stroke="#3b82f6"
                        strokeWidth={3}
                        dot={false}
                        name="Wind"
                        animationDuration={1500}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export const PlantBarChart = ({ data }: ChartProps) => {
    const COLORS = ['#3b82f6', '#22c55e', '#a855f7', '#f59e0b'];

    return (
        <div className="bg-card p-6 rounded-xl border" style={{ height: '400px' }}>
            <h3 className="font-bold mb-6">Efficiency by Plant (%)</h3>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                    <XAxis dataKey="plant_id" stroke="#a1a1aa" fontSize={12} />
                    <YAxis stroke="#a1a1aa" fontSize={12} domain={[0, 100]} />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px' }}
                    />
                    <Bar dataKey="efficiency" radius={[4, 4, 0, 0]} animationDuration={1500}>
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};
