"use client";

import { useState, useEffect } from "react";
import { useVidyaContext } from "@/providers/VidyaContextProvider";

export function useOnlineStatus() {
    const [isOnline, setIsOnline] = useState(true); // default true for SSR
    const { setOfflineMode } = useVidyaContext();

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setIsOnline(navigator.onLine);
        setOfflineMode(!navigator.onLine);

        const handleOnline = () => {
            setIsOnline(true);
            setOfflineMode(false);
        };
        const handleOffline = () => {
            setIsOnline(false);
            setOfflineMode(true);
        };

        window.addEventListener("online", handleOnline);
        window.addEventListener("offline", handleOffline);

        return () => {
            window.removeEventListener("online", handleOnline);
            window.removeEventListener("offline", handleOffline);
        };
    }, [setOfflineMode]);

    return isOnline;
}
