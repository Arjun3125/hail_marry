"use client";

import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import {
    LayoutDashboard,
    CalendarCheck,
    Award,
    FileText,
    Settings,
} from "lucide-react";
import { MascotLauncher } from "@/components/mascot/MascotLauncher";
import { MobileBottomNav } from "@/components/ui/SharedUI";
import { ContextBar } from "@/components/ContextBar";

const mobileNav = [
    { label: "Dashboard", href: "/parent/dashboard", icon: LayoutDashboard },
    { label: "Attendance", href: "/parent/attendance", icon: CalendarCheck },
    { label: "Marks", href: "/parent/results", icon: Award },
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
    return (
        <div className="flex min-h-screen bg-[var(--bg-page)]">
            <Sidebar items={parentNav} role="parent" />
            <main className="flex-1 min-w-0 p-4 pt-16 sm:p-5 sm:pt-16 lg:p-6 lg:pt-6 has-bottom-nav">
                <div className="mx-auto flex max-w-7xl flex-col gap-4">
                    <ContextBar role="parent" items={parentNav} />
                    {children}
                </div>
            </main>
            {pathname !== "/parent/assistant" ? <MascotLauncher role="parent" /> : null}
            <MobileBottomNav items={mobileNav} currentPath={pathname} />
        </div>
    );
}
