"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { api } from "@/lib/api";
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
    Sparkles,
    QrCode,
    ShieldAlert,
    Palette,
} from "lucide-react";

const adminNav = [
    { label: "School Health", href: "/admin/dashboard", icon: LayoutDashboard, group: "Control" },
    { label: "Setup Wizard", href: "/admin/setup-wizard", icon: Sparkles, group: "Control" },
    { label: "People", href: "/admin/users", icon: Users, group: "People" },
    { label: "Classes", href: "/admin/classes", icon: BookOpen, group: "People" },
    { label: "Timetable", href: "/admin/timetable", icon: Calendar, group: "People" },
    { label: "Complaints", href: "/admin/complaints", icon: MessageSquare, group: "People" },
    { label: "QR Cards", href: "/admin/qr-cards", icon: QrCode, group: "People" },
    { label: "Performance", href: "/admin/reports", icon: FileText, group: "Performance" },
    { label: "AI Usage", href: "/admin/ai-usage", icon: BarChart3, group: "Performance" },
    { label: "AI Review", href: "/admin/ai-review", icon: Bot, group: "Performance" },
    { label: "Operations", href: "/admin/queue", icon: Activity, group: "Operations" },
    { label: "Traces", href: "/admin/traces", icon: ScanSearch, group: "Operations" },
    { label: "Security", href: "/admin/security", icon: Shield, group: "Operations" },
    { label: "Webhooks", href: "/admin/webhooks", icon: Webhook, group: "Operations" },
    { label: "Billing", href: "/admin/billing", icon: CreditCard, group: "Operations" },
    { label: "Features", href: "/admin/feature-flags", icon: ShieldAlert, group: "Operations" },
    { label: "Branding", href: "/admin/branding", icon: Palette, group: "Operations" },
    { label: "Settings", href: "/admin/settings", icon: Settings, utility: true },
];

import GuidedTour, { adminTourSteps } from "@/components/GuidedTour";
import { MascotLauncher } from "@/components/mascot/MascotLauncher";
import { MobileBottomNav } from "@/components/ui/SharedUI";
import { ContextBar } from "@/components/ContextBar";

const mobileNav = [
    { label: "Dashboard", href: "/admin/dashboard", icon: LayoutDashboard },
    { label: "Users", href: "/admin/users", icon: Users },
    { label: "Classes", href: "/admin/classes", icon: BookOpen },
    { label: "Queue", href: "/admin/queue", icon: Activity },
    { label: "Assistant", href: "/admin/assistant", icon: Bot },
];


export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const [hasBadge, setHasBadge] = useState(false);
    useEffect(() => {
        api.mascot
            .greeting()
            .then((res: { has_urgent?: boolean }) => setHasBadge(Boolean(res.has_urgent)))
            .catch(() => {/* badge stays false */});
    }, []);
    return (
        <div className="flex min-h-dvh bg-[var(--bg-page)]">
            <Sidebar items={adminNav} role="admin" />
            <main className="flex-1 min-w-0 p-4 sm:p-5 lg:p-6 lg:pt-6 has-bottom-nav" style={{ paddingTop: 'calc(var(--mobile-header-height) + 0.5rem)' }}>
                <div className="mx-auto flex max-w-7xl flex-col gap-4">
                    <ContextBar role="admin" items={adminNav} />
                    {children}
                </div>
            </main>
            <GuidedTour steps={adminTourSteps} storageKey="admin-tour" />
            {pathname !== "/admin/assistant" ? <MascotLauncher role="admin" hasBadge={hasBadge} /> : null}
            <MobileBottomNav items={mobileNav} currentPath={pathname} />
        </div>
    );
}
