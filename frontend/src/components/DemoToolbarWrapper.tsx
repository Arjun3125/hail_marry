"use client";

import DemoToolbar from "./DemoToolbar";
import { ToastProvider } from "./Toast";

export default function DemoToolbarWrapper() {
    const isDemoMode = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

    return (
        <ToastProvider>
            {isDemoMode && <DemoToolbar />}
        </ToastProvider>
    );
}
