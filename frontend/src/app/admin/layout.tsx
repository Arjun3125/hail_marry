"use client";

import Sidebar from "@/components/Sidebar";
import {
    LayoutDashboard,
    Users,
    BarChart3,
    Activity,
    Shield,
    ScanSearch,
    Bot,
    MessageSquare,
    CreditCard,
    Settings,
    BookOpen,
    Calendar,
    FileText,
    Webhook,
} from "lucide-react";

const adminNav = [
    { label: "Dashboard", href: "/admin/dashboard", icon: LayoutDashboard },
    { label: "Users", href: "/admin/users", icon: Users },
    { label: "Classes", href: "/admin/classes", icon: BookOpen },
    { label: "Timetable", href: "/admin/timetable", icon: Calendar },
    { label: "AI Usage", href: "/admin/ai-usage", icon: BarChart3 },
    { label: "AI Review", href: "/admin/ai-review", icon: Bot },
    { label: "AI Queue", href: "/admin/queue", icon: Activity },
    { label: "Traces", href: "/admin/traces", icon: ScanSearch },
    { label: "Complaints", href: "/admin/complaints", icon: MessageSquare },
    { label: "Reports", href: "/admin/reports", icon: FileText },
    { label: "Security", href: "/admin/security", icon: Shield },
    { label: "Webhooks", href: "/admin/webhooks", icon: Webhook },
    { label: "Billing", href: "/admin/billing", icon: CreditCard },
    { label: "Settings", href: "/admin/settings", icon: Settings },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex min-h-screen bg-[var(--bg-page)]">
            <Sidebar items={adminNav} role="admin" />
            <main className="flex-1 min-w-0 p-4 pt-16 sm:p-5 sm:pt-16 lg:p-6 lg:pt-6">
                <div className="mx-auto max-w-7xl">{children}</div>
            </main>
        </div>
    );
}
