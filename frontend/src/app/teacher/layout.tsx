"use client";

import { usePathname } from "next/navigation";
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
    Bot,
} from "lucide-react";

const teacherNav = [
    { label: "My Classes", href: "/teacher/dashboard", icon: LayoutDashboard, group: "My Day" },
    { label: "Classes", href: "/teacher/classes", icon: Users, group: "My Day" },
    { label: "Attendance", href: "/teacher/attendance", icon: CalendarCheck, group: "Workflow" },
    { label: "Assessments", href: "/teacher/generate-assessment", icon: ClipboardList, group: "Workflow" },
    { label: "Homework", href: "/teacher/assignments", icon: FileText, group: "Workflow" },
    { label: "Marks Entry", href: "/teacher/marks", icon: Award, group: "Workflow" },
    { label: "Study Materials", href: "/teacher/upload", icon: Upload, group: "Resources" },
    { label: "Source Discovery", href: "/teacher/discover", icon: Globe, group: "Resources" },
    { label: "Insights", href: "/teacher/insights", icon: BarChart3, group: "Insights" },
    { label: "Doubt Heatmap", href: "/teacher/doubt-heatmap", icon: Flame, group: "Insights" },
    { label: "Profile", href: "/teacher/profile", icon: User, utility: true },
];
import GuidedTour, { teacherTourSteps } from "@/components/GuidedTour";
import { MascotLauncher } from "@/components/mascot/MascotLauncher";
import { MobileBottomNav } from "@/components/ui/SharedUI";
import { ContextBar } from "@/components/ContextBar";

const mobileNav = [
    { label: "Dashboard", href: "/teacher/dashboard", icon: LayoutDashboard },
    { label: "Classes", href: "/teacher/classes", icon: Users },
    { label: "Attendance", href: "/teacher/attendance", icon: CalendarCheck },
    { label: "Upload", href: "/teacher/upload", icon: Upload },
    { label: "Assistant", href: "/teacher/assistant", icon: Bot },
];


export default function TeacherLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    return (
        <div className="flex min-h-screen bg-[var(--bg-page)]">
            <Sidebar items={teacherNav} role="teacher" />
            <main className="flex-1 min-w-0 p-4 pt-16 sm:p-5 sm:pt-16 lg:p-6 lg:pt-6 has-bottom-nav">
                <div className="mx-auto flex max-w-7xl flex-col gap-4">
                    <ContextBar role="teacher" items={teacherNav} />
                    {children}
                </div>
            </main>
            <GuidedTour steps={teacherTourSteps} storageKey="teacher-tour" />
            {pathname !== "/teacher/assistant" ? <MascotLauncher role="teacher" /> : null}
            <MobileBottomNav items={mobileNav} currentPath={pathname} />
        </div>
    );
}
