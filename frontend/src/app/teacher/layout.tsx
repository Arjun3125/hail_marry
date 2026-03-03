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
    { label: "Profile", href: "/teacher/profile", icon: User },
];

export default function TeacherLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="min-h-screen bg-slate-50">
            <Sidebar items={teacherNav} role="teacher" />
            <main className="ml-60 p-6">{children}</main>
        </div>
    );
}
