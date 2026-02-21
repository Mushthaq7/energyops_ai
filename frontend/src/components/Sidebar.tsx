"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    MessageSquare,
    Activity,
    Settings,
    Zap
} from "lucide-react";

const Sidebar = () => {
    const pathname = usePathname();

    const navItems = [
        { name: "Dashboard", href: "/", icon: LayoutDashboard },
        { name: "RAG Chat", href: "/chat", icon: MessageSquare },
        { name: "Monitoring", href: "/monitoring", icon: Activity },
    ];

    return (
        <aside className="bg-card border-r" style={{ width: '260px', padding: '1.5rem' }}>
            <div className="flex items-center gap-2 mb-8" style={{ color: 'var(--primary)', fontWeight: 'bold', fontSize: '1.25rem' }}>
                <Zap fill="currentColor" size={24} />
                <span>EnergyOps AI</span>
            </div>

            <nav className="flex flex-col gap-2">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-4 p-3 rounded-xl transition-colors ${isActive
                                    ? "bg-primary text-primary-foreground"
                                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                                }`}
                        >
                            <Icon size={20} />
                            <span className="font-medium">{item.name}</span>
                        </Link>
                    );
                })}
            </nav>

            <div style={{ marginTop: 'auto', paddingTop: '1.5rem', borderTop: '1px solid var(--border)' }}>
                <div className="flex items-center gap-4 p-3 text-muted-foreground hover:text-foreground cursor-pointer transition-colors">
                    <Settings size={20} />
                    <span className="font-medium">Settings</span>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
