"use client";

import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import {
    LayoutDashboard,
    CalendarCheck,
    Award,
    FileText,
} from "lucide-react";
import { MascotLauncher } from "@/components/mascot/MascotLauncher";

const parentNav = [
    { label: "Dashboard", href: "/parent/dashboard", icon: LayoutDashboard },
    { label: "Attendance", href: "/parent/attendance", icon: CalendarCheck },
    { label: "Results", href: "/parent/results", icon: Award },
    { label: "Reports", href: "/parent/reports", icon: FileText },
];

export default function ParentLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    return (
        <div className="flex min-h-screen bg-[var(--bg-page)]">
            <Sidebar items={parentNav} role="parent" />
            <main className="flex-1 min-w-0 p-4 pt-16 sm:p-5 sm:pt-16 lg:p-6 lg:pt-6">
                <div className="mx-auto max-w-7xl">{children}</div>
            </main>
            {pathname !== "/parent/assistant" ? <MascotLauncher role="parent" /> : null}
        </div>
    );
}
