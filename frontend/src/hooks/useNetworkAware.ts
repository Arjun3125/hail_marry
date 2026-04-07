/**
 * useNetworkAware - Adaptive loading hook for low-bandwidth scenarios.
 *
 * Detects the user's effective connection type (2G/3G/4G) via the
 * Network Information API and provides flags to conditionally disable
 * heavy assets (Three.js scenes, background polling, large images).
 */
"use client";

import { useCallback, useEffect, useState } from "react";

type EffectiveType = "slow-2g" | "2g" | "3g" | "4g" | "unknown";

interface NetworkAwareState {
    isSlowConnection: boolean;
    effectiveType: EffectiveType;
    saveData: boolean;
    downlinkMbps: number;
}

interface NetworkInformation extends EventTarget {
    effectiveType?: string;
    saveData?: boolean;
    downlink?: number;
    addEventListener(type: string, listener: EventListener): void;
    removeEventListener(type: string, listener: EventListener): void;
}

declare global {
    interface Navigator {
        connection?: NetworkInformation;
        mozConnection?: NetworkInformation;
        webkitConnection?: NetworkInformation;
    }
}

function getConnection(): NetworkInformation | undefined {
    if (typeof navigator === "undefined") return undefined;
    return navigator.connection || navigator.mozConnection || navigator.webkitConnection;
}

function readState(conn: NetworkInformation | undefined): NetworkAwareState {
    if (!conn) {
        return {
            isSlowConnection: false,
            effectiveType: "unknown",
            saveData: false,
            downlinkMbps: 0,
        };
    }

    const effectiveType = (conn.effectiveType as EffectiveType) || "unknown";
    const saveData = conn.saveData ?? false;
    const downlinkMbps = conn.downlink ?? 0;
    const isSlowConnection =
        saveData ||
        effectiveType === "slow-2g" ||
        effectiveType === "2g" ||
        effectiveType === "3g";

    return { isSlowConnection, effectiveType, saveData, downlinkMbps };
}

export function useNetworkAware(): NetworkAwareState {
    const [state, setState] = useState<NetworkAwareState>(() => readState(getConnection()));

    const handleChange = useCallback(() => {
        setState(readState(getConnection()));
    }, []);

    useEffect(() => {
        const connection = getConnection();
        if (!connection) return;

        connection.addEventListener("change", handleChange);
        return () => connection.removeEventListener("change", handleChange);
    }, [handleChange]);

    return state;
}
