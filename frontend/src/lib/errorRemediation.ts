export type ErrorKind = "network" | "auth" | "validation" | "server" | "unknown";

export type ErrorRemediationMeta = {
    kind: ErrorKind;
    title: string;
    actionLabel: string;
    helpText: string;
};

const remediationByKind: Record<ErrorKind, Omit<ErrorRemediationMeta, "kind">> = {
    network: {
        title: "Network issue",
        actionLabel: "Retry now",
        helpText: "Check internet/VPN connectivity and try again.",
    },
    auth: {
        title: "Session issue",
        actionLabel: "Retry now",
        helpText: "Your session may have expired. Retry, then sign in again if needed.",
    },
    validation: {
        title: "Input issue",
        actionLabel: "Retry now",
        helpText: "Review your recent inputs and retry with valid values.",
    },
    server: {
        title: "Server issue",
        actionLabel: "Retry now",
        helpText: "The service is temporarily unavailable. Retry in a few seconds.",
    },
    unknown: {
        title: "Unexpected issue",
        actionLabel: "Retry now",
        helpText: "Please retry. If it continues, share the support IDs below.",
    },
};

const normalize = (error: string) => error.toLowerCase();

export function classifyError(error: string): ErrorRemediationMeta {
    const message = normalize(error);

    const kind: ErrorKind =
        message.includes("network") || message.includes("failed to fetch") || message.includes("timeout")
            ? "network"
            : message.includes("unauthorized") || message.includes("forbidden") || message.includes("token") || message.includes("session")
                ? "auth"
                : message.includes("invalid") || message.includes("missing") || message.includes("required")
                    ? "validation"
                    : message.includes("500") || message.includes("503") || message.includes("server")
                        ? "server"
                        : "unknown";

    return { kind, ...remediationByKind[kind] };
}

function shortHash(input: string): string {
    let hash = 0;
    for (let i = 0; i < input.length; i += 1) {
        hash = (hash << 5) - hash + input.charCodeAt(i);
        hash |= 0;
    }
    return Math.abs(hash).toString(16).slice(0, 8).toUpperCase();
}

export function supportIds(scope: string, error: string) {
    const base = `${scope}:${error}`;
    return {
        traceId: `TRC-${shortHash(base + ":trace")}`,
        refId: `REF-${shortHash(base + ":ref")}`,
    };
}
