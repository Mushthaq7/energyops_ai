import { LucideIcon } from "lucide-react";

interface StatsCardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    trend?: string;
    color?: string;
}

const StatsCard = ({ title, value, icon: Icon, trend, color = "var(--primary)" }: StatsCardProps) => {
    return (
        <div className="bg-card p-6 rounded-xl border animate-fade-in">
            <div className="flex justify-between items-start mb-4">
                <div style={{ color: color }} className="p-2 bg-secondary rounded-lg">
                    <Icon size={24} />
                </div>
                {trend && (
                    <span className="text-sm font-medium" style={{ color: trend.startsWith("+") ? "var(--accent)" : "var(--destructive)" }}>
                        {trend}
                    </span>
                )}
            </div>
            <div>
                <p className="text-muted text-sm mb-1">{title}</p>
                <h3 className="text-2xl font-bold">{value}</h3>
            </div>
        </div>
    );
};

export default StatsCard;
