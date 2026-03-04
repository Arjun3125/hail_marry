"use client";

import Sidebar from "@/components/Sidebar";
import {
    LayoutDashboard,
    Users,
    BarChart3,
    Shield,
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
    { label: "Complaints", href: "/admin/complaints", icon: MessageSquare },
    { label: "Reports", href: "/admin/reports", icon: FileText },
    { label: "Security", href: "/admin/security", icon: Shield },
    { label: "Webhooks", href: "/admin/webhooks", icon: Webhook },
    { label: "Billing", href: "/admin/billing", icon: CreditCard },
    { label: "Settings", href: "/admin/settings", icon: Settings },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="min-h-screen bg-slate-50">
            <Sidebar items={adminNav} role="admin" />
            <main className="ml-60 p-6">{children}</main>
        </div>
    );
}
