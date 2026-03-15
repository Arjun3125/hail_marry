import { Suspense } from "react";

import TeacherAttendanceClient from "./AttendanceClient";

export default function TeacherAttendancePage() {
    return (
        <Suspense fallback={<div className="text-sm text-[var(--text-muted)]">Loading attendance…</div>}>
            <TeacherAttendanceClient />
        </Suspense>
    );
}
