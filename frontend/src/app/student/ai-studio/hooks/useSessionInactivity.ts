import { useEffect, useRef, useCallback, useState } from "react";

const INACTIVITY_TIMEOUT = 5 * 60 * 1000; // 5 minutes

export function useSessionInactivity(onTimeout: () => void) {
    const inactivityTimerRef = useRef<NodeJS.Timeout | null>(null);
    const isInactiveRef = useRef(false);
    const [isInactive, setIsInactive] = useState(false);

    const resetTimer = useCallback(() => {
        if (inactivityTimerRef.current) {
            clearTimeout(inactivityTimerRef.current);
        }

        inactivityTimerRef.current = setTimeout(() => {
            isInactiveRef.current = true;
            setIsInactive(true);
            onTimeout();
        }, INACTIVITY_TIMEOUT);
    }, [onTimeout]);

    useEffect(() => {
        resetTimer();

        const handleActivity = () => {
            if (!isInactiveRef.current) {
                resetTimer();
                return;
            }
            isInactiveRef.current = false;
            setIsInactive(false);
            resetTimer();
        };

        window.addEventListener("mousemove", handleActivity);
        window.addEventListener("keydown", handleActivity);
        window.addEventListener("click", handleActivity);
        window.addEventListener("scroll", handleActivity);
        window.addEventListener("touchstart", handleActivity);

        return () => {
            window.removeEventListener("mousemove", handleActivity);
            window.removeEventListener("keydown", handleActivity);
            window.removeEventListener("click", handleActivity);
            window.removeEventListener("scroll", handleActivity);
            window.removeEventListener("touchstart", handleActivity);

            if (inactivityTimerRef.current) {
                clearTimeout(inactivityTimerRef.current);
            }
        };
    }, [resetTimer]);

    return {
        isInactive,
        resetTimer,
    };
}
