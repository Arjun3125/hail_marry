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
    RotateCcw,
    MessageSquare,
    User,
    Headphones,
    Presentation,
    Network,
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
    { label: "Mind Map", href: "/student/mind-map", icon: Network },
    { label: "Audio Overview", href: "/student/audio-overview", icon: Headphones },
    { label: "Video Overview", href: "/student/video-overview", icon: Presentation },
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
        <div className="flex min-h-screen bg-slate-50">
            <Sidebar items={studentNav} role="student" />
            <main className="flex-1 min-w-0 p-4 pt-16 sm:p-5 sm:pt-16 lg:p-6 lg:pt-6">
                <div className="mx-auto max-w-7xl">{children}</div>
            </main>
        </div>
    );
}
