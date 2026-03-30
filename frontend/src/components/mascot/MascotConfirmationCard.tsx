"use client";

import { MascotResponse } from "./types";

export function MascotConfirmationCard({
    response,
    onDecision,
    loading,
}: {
    response: MascotResponse;
    onDecision: (approved: boolean) => void;
    loading?: boolean;
}) {
    if (!response.requires_confirmation || !response.confirmation_id) return null;
    return (
        <div className="mt-3 rounded-2xl border border-amber-400/40 bg-amber-50/80 p-3 text-xs text-amber-950 dark:bg-amber-500/10 dark:text-amber-100">
            <p className="font-semibold">Confirmation required</p>
            <p className="mt-1">This request changes saved data. Confirm to continue or cancel to stop.</p>
            <div className="mt-3 flex gap-2">
                <button
                    type="button"
                    disabled={loading}
                    onClick={() => onDecision(true)}
                    className="rounded-lg bg-amber-600 px-3 py-2 font-semibold text-white disabled:opacity-60"
                >
                    Confirm
                </button>
                <button
                    type="button"
                    disabled={loading}
                    onClick={() => onDecision(false)}
                    className="rounded-lg border border-amber-500/40 px-3 py-2 font-semibold text-amber-900 disabled:opacity-60 dark:text-amber-100"
                >
                    Cancel
                </button>
            </div>
        </div>
    );
}

