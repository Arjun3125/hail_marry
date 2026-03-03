"use client";

import Sidebar from "@/components/Sidebar";
import {
    LayoutDashboard,
    CalendarCheck,
    Award,
    FileText,
    Calendar,
    BookOpen,
    Upload,
    Bot,
    Sparkles,
    MessageSquare,
    RotateCcw,
    User,
} from "lucide-react";

const studentNav = [
    { label: "Overview", href: "/student/overview", icon: LayoutDashboard },
    { label: "Attendance", href: "/student/attendance", icon: CalendarCheck },
    { label: "Results", href: "/student/results", icon: Award },
    { label: "Assignments", href: "/student/assignments", icon: FileText },
    { label: "Timetable", href: "/student/timetable", icon: Calendar },
    { label: "Lectures", href: "/student/lectures", icon: BookOpen },
    { label: "Upload", href: "/student/upload", icon: Upload },
    { label: "AI Assistant", href: "/student/ai", icon: Bot },
    { label: "Study Tools", href: "/student/tools", icon: Sparkles },
    { label: "Reviews", href: "/student/reviews", icon: RotateCcw },
    { label: "Complaints", href: "/student/complaints", icon: MessageSquare },
    { label: "Profile", href: "/student/profile", icon: User },
];

export default function StudentLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-slate-50">
            <Sidebar items={studentNav} role="student" />
            <main className="ml-60 p-6">{children}</main>
        </div>
    );
}
