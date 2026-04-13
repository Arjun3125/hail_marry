"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { logger } from "@/lib/logger";

interface VidyaContextState {
    activeSubject: string | null;
    activeClassId: string | null;
    activeClassLabel: string | null;
    lastAITopic: string | null;
    lastRole: string | null;
    isOfflineMode: boolean;
}

interface VidyaContextActions {
    setActiveSubject: (subject: string | null) => void;
    setActiveClassId: (classId: string | null) => void;
    setActiveClassLabel: (label: string | null) => void;
    setLastAITopic: (topic: string | null) => void;
    setLastRole: (role: string | null) => void;
    setOfflineMode: (isOffline: boolean) => void;
    mergeContext: (partial: Partial<VidyaContextState>) => void;
}

type VidyaContextType = VidyaContextState & VidyaContextActions;

const defaultState: VidyaContextState = {
    activeSubject: null,
    activeClassId: null,
    activeClassLabel: null,
    lastAITopic: null,
    lastRole: null,
    isOfflineMode: false,
};

const VidyaContext = createContext<VidyaContextType | undefined>(undefined);

export function VidyaContextProvider({ children }: { children: React.ReactNode }) {
    const [state, setState] = useState<VidyaContextState>(defaultState);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        // Load from localStorage on mount
        try {
            const stored = localStorage.getItem("vidyaContext");
            if (stored) {
                const parsed = JSON.parse(stored);
                // eslint-disable-next-line react-hooks/set-state-in-effect
                setState((prev) => ({ ...prev, ...parsed }));
            }
        } catch (e) {
            logger.error("Failed to load VidyaContext:", e as Error);
        }
        setMounted(true);
    }, []);

    // Save to localStorage when state changes (only core string fields, not ephemeral UI states)
    useEffect(() => {
        if (!mounted) return;
        try {
            localStorage.setItem("vidyaContext", JSON.stringify({
                activeSubject: state.activeSubject,
                activeClassId: state.activeClassId,
                activeClassLabel: state.activeClassLabel,
                lastAITopic: state.lastAITopic,
                lastRole: state.lastRole,
            }));
        } catch (e) {
            logger.error("Failed to save VidyaContext:", e as Error);
        }
    }, [state.activeSubject, state.activeClassId, state.activeClassLabel, state.lastAITopic, state.lastRole, mounted]);

    const setActiveSubject = useCallback((subject: string | null) => {
        setState((prev) => ({ ...prev, activeSubject: subject }));
    }, []);

    const setActiveClassId = useCallback((classId: string | null) => {
        setState((prev) => ({ ...prev, activeClassId: classId }));
    }, []);

    const setActiveClassLabel = useCallback((label: string | null) => {
        setState((prev) => ({ ...prev, activeClassLabel: label }));
    }, []);

    const setLastAITopic = useCallback((topic: string | null) => {
        setState((prev) => ({ ...prev, lastAITopic: topic }));
    }, []);

    const setLastRole = useCallback((role: string | null) => {
        setState((prev) => ({ ...prev, lastRole: role }));
    }, []);

    const setOfflineMode = useCallback((isOffline: boolean) => {
        setState((prev) => ({ ...prev, isOfflineMode: isOffline }));
    }, []);

    const mergeContext = useCallback((partial: Partial<VidyaContextState>) => {
        setState((prev) => ({ ...prev, ...partial }));
    }, []);

    const actions: VidyaContextActions = useMemo(() => ({
        setActiveSubject,
        setActiveClassId,
        setActiveClassLabel,
        setLastAITopic,
        setLastRole,
        setOfflineMode,
        mergeContext,
    }), [mergeContext, setActiveClassId, setActiveClassLabel, setActiveSubject, setLastAITopic, setLastRole, setOfflineMode]);

    const value = useMemo(
        () => ({ ...state, ...actions }),
        [actions, state],
    );

    return (
        <VidyaContext.Provider value={value}>
            {children}
        </VidyaContext.Provider>
    );
}

export function useVidyaContext() {
    const context = useContext(VidyaContext);
    if (context === undefined) {
        throw new Error("useVidyaContext must be used within a VidyaContextProvider");
    }
    return context;
}
