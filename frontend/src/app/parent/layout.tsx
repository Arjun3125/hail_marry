"use client";

import Sidebar from "@/components/Sidebar";
import {
    LayoutDashboard,
    CalendarCheck,
    Award,
    FileText,
} from "lucide-react";

const parentNav = [
    { label: "Dashboard", href: "/parent/dashboard", icon: LayoutDashboard },
    { label: "Attendance", href: "/parent/attendance", icon: CalendarCheck },
    { label: "Results", href: "/parent/results", icon: Award },
    { label: "Reports", href: "/parent/reports", icon: FileText },
];

export default function ParentLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="min-h-screen bg-slate-50">
            <Sidebar items={parentNav} role="parent" />
            <main className="ml-60 p-6">{children}</main>
        </div>
    );
}
