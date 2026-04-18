"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { api } from "@/lib/api";
import Sidebar from "@/components/Sidebar";
import {
    LayoutDashboard,
    CalendarCheck,
    Award,
    FileText,
    Settings,
    Bot,
} from "lucide-react";
import { MascotLauncher } from "@/components/mascot/MascotLauncher";
import { MobileBottomNav } from "@/components/ui/SharedUI";
import { ContextBar } from "@/components/ContextBar";

const mobileNav = [
    { label: "Dashboard", href: "/parent/dashboard", icon: LayoutDashboard },
    { label: "Attendance", href: "/parent/attendance", icon: CalendarCheck },
    { label: "Results", href: "/parent/results", icon: Award },
    { label: "Reports", href: "/parent/reports", icon: FileText },
    { label: "Assistant", href: "/parent/assistant", icon: Bot },
];


const parentNav = [
    { label: "Dashboard", href: "/parent/dashboard", icon: LayoutDashboard, group: "Overview" },
    { label: "Attendance", href: "/parent/attendance", icon: CalendarCheck, group: "Track" },
    { label: "Marks & Progress", href: "/parent/results", icon: Award, group: "Track" },
    { label: "Reports", href: "/parent/reports", icon: FileText, group: "Track" },
    { label: "Notification Settings", href: "/parent/settings", icon: Settings, group: "Settings" },
];

export default function ParentLayout({ children }: { children: React.ReactNode }) {
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
            <Sidebar items={parentNav} role="parent" />
            <main className="flex-1 min-w-0 p-4 sm:p-5 lg:p-6 lg:pt-6 has-bottom-nav" style={{ paddingTop: 'calc(var(--mobile-header-height) + 0.5rem)' }}>
                <div className="mx-auto flex max-w-7xl flex-col gap-4">
                    <ContextBar role="parent" items={parentNav} />
                    {children}
                </div>
            </main>
            {pathname !== "/parent/assistant" ? <MascotLauncher role="parent" hasBadge={hasBadge} /> : null}
            <MobileBottomNav items={mobileNav} currentPath={pathname} />
        </div>
    );
}
