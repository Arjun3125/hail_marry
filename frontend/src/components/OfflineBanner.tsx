"use client";

import { useState } from "react";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { WifiOff, ChevronDown } from "lucide-react";

export function OfflineBanner() {
    const isOnline = useOnlineStatus();
    const [expanded, setExpanded] = useState(false);

    if (isOnline) return null;

    return (
        <div className="fixed top-0 left-0 right-0 z-[100] bg-status-orange shadow-md">
            <div className="flex items-center justify-between gap-2 px-4 py-1.5">
                <div className="flex items-center gap-2">
                    <WifiOff className="h-4 w-4 text-white" />
                    <span className="text-xs font-semibold text-white">You&apos;re offline. Viewing cached data. Changes will sync when reconnected.</span>
                </div>
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="ml-auto flex items-center gap-1 rounded px-2 py-1 text-xs font-semibold text-white hover:bg-status-orange-dark transition"
                >
                    Available
                    <ChevronDown className={`h-3 w-3 transition ${expanded ? "rotate-180" : ""}`} />
                </button>
            </div>

            {expanded && (
                <div className="border-t border-status-orange-dark bg-status-orange px-4 py-2 text-xs text-white">
                    <p className="mb-2 font-semibold">Available offline:</p>
                    <div className="grid gap-2 sm:grid-cols-2 md:grid-cols-3">
                        <div>
                            <p className="font-semibold">Student</p>
                            <ul className="text-[11px] leading-5 opacity-90">
                                <li>✓ Attendance log</li>
                                <li>✓ Assignments list</li>
                                <li>✓ Timetable</li>
                                <li>✓ Results & marks</li>
                            </ul>
                        </div>
                        <div>
                            <p className="font-semibold">Teacher</p>
                            <ul className="text-[11px] leading-5 opacity-90">
                                <li>✓ Classes list</li>
                                <li>✓ Past attendance</li>
                                <li>✓ Assignment details</li>
                            </ul>
                        </div>
                        <div>
                            <p className="font-semibold">Parent</p>
                            <ul className="text-[11px] leading-5 opacity-90">
                                <li>✓ Child attendance</li>
                                <li>✓ Test results</li>
                                <li>✓ Dashboard</li>
                            </ul>
                        </div>
                    </div>
                    <p className="mt-2 text-[10px] opacity-75">Internet connection needed for: AI Studio, creating submissions, viewing live data.</p>
                </div>
            )}
        </div>
    );
}
