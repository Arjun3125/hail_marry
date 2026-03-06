"use client";

import Sidebar from "@/components/Sidebar";
import {
    LayoutDashboard,
    Users,
    CalendarCheck,
    Award,
    FileText,
    Upload,
    BarChart3,
    ClipboardList,
    Flame,
    Globe,
    User,
} from "lucide-react";

const teacherNav = [
    { label: "Dashboard", href: "/teacher/dashboard", icon: LayoutDashboard },
    { label: "Classes", href: "/teacher/classes", icon: Users },
    { label: "Attendance", href: "/teacher/attendance", icon: CalendarCheck },
    { label: "Marks Entry", href: "/teacher/marks", icon: Award },
    { label: "Assignments", href: "/teacher/assignments", icon: FileText },
    { label: "Upload Notes", href: "/teacher/upload", icon: Upload },
    { label: "AI Insights", href: "/teacher/insights", icon: BarChart3 },
    { label: "Assessment Gen", href: "/teacher/generate-assessment", icon: ClipboardList },
    { label: "Doubt Heatmap", href: "/teacher/doubt-heatmap", icon: Flame },
    { label: "Source Discovery", href: "/teacher/discover", icon: Globe },
    { label: "Profile", href: "/teacher/profile", icon: User },
];

export default function TeacherLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex min-h-screen bg-slate-50">
            <Sidebar items={teacherNav} role="teacher" />
            <main className="flex-1 min-w-0 p-4 pt-16 sm:p-5 sm:pt-16 lg:p-6 lg:pt-6">
                <div className="mx-auto max-w-7xl">{children}</div>
            </main>
        </div>
    );
}
