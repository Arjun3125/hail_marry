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
    Calendar,
    BookOpen,
    Upload,
    RotateCcw,
    MessageSquare,
    User,
    Headphones,
    Presentation,
    Network,
    Trophy,
    Library,
    Wand2,
    Target,
    Bot,
    ClipboardList,
} from "lucide-react";
import GuidedTour, { studentTourSteps } from "@/components/GuidedTour";
import { MobileBottomNav } from "@/components/ui/SharedUI";
import { MascotLauncher } from "@/components/mascot/MascotLauncher";
import { OnboardingGate } from "@/components/OnboardingGate";
import { ContextBar } from "@/components/ContextBar";


const studentNav = [
    { label: "Overview", href: "/student/overview", icon: LayoutDashboard, group: "Study" },
    { label: "AI Studio", href: "/student/ai-studio", icon: Wand2, group: "Study" },
    { label: "Mind Map", href: "/student/mind-map", icon: Network, group: "Study" },
    { label: "Mastery Map", href: "/student/mastery", icon: Target, group: "Study" },
    { label: "AI Library", href: "/student/ai-library", icon: Library, group: "Study" },
    { label: "Your Work", href: "/student/assignments", icon: FileText, group: "Work" },
    { label: "Timetable", href: "/student/timetable", icon: Calendar, group: "Work" },
    { label: "Lectures", href: "/student/lectures", icon: BookOpen, group: "Work" },
    { label: "Add Study Material", href: "/student/upload", icon: Upload, group: "Work" },
    { label: "Audio Overview", href: "/student/audio-overview", icon: Headphones, group: "Work" },
    { label: "Video Overview", href: "/student/video-overview", icon: Presentation, group: "Work" },
    { label: "Attendance", href: "/student/attendance", icon: CalendarCheck, group: "Track" },
    { label: "Marks & Progress", href: "/student/results", icon: Award, group: "Track" },
    { label: "Reviews", href: "/student/reviews", icon: RotateCcw, group: "Track" },
    { label: "Class Rankings", href: "/student/leaderboard", icon: Trophy, group: "Track" },
    { label: "Report an Issue", href: "/student/complaints", icon: MessageSquare, group: "Connect" },
    { label: "Profile", href: "/student/profile", icon: User, utility: true },
];

const mobileNav = [
    { label: "Overview", href: "/student/overview", icon: LayoutDashboard },
    { label: "AI Studio", href: "/student/ai-studio", icon: Wand2 },
    { label: "Assignments", href: "/student/assignments", icon: ClipboardList },
    { label: "Upload", href: "/student/upload", icon: Upload },
    { label: "Assistant", href: "/student/assistant", icon: Bot },
];

export default function StudentLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const showMascotLauncher = pathname !== "/student/assistant";
    const [hasBadge, setHasBadge] = useState(false);
    useEffect(() => {
        api.mascot
            .greeting()
            .then((res: any) => setHasBadge(Boolean(res.has_urgent)))
            .catch(() => {/* badge stays false */});
    }, []);
    return (
        <OnboardingGate>
            <div className="flex min-h-screen bg-[var(--bg-page)]">
                <Sidebar items={studentNav} role="student" />
                <main className="flex-1 min-w-0 p-4 pt-16 sm:p-5 sm:pt-16 lg:p-6 lg:pt-6 has-bottom-nav">
                    <div className="mx-auto flex max-w-7xl flex-col gap-4">
                        <ContextBar role="student" items={studentNav} />
                        {children}
                    </div>
                </main>
                <GuidedTour steps={studentTourSteps} storageKey="student-tour" />
                {showMascotLauncher ? <MascotLauncher role="student" hasBadge={hasBadge} /> : null}
                <MobileBottomNav items={mobileNav} currentPath={pathname} />
            </div>
        </OnboardingGate>
    );
}
