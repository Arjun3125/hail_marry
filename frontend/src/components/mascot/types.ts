export type MascotAction = {
    kind: string;
    status: string;
    payload?: Record<string, unknown>;
    result_summary?: string | null;
};

export type MascotResponse = {
    reply_text: string;
    intent: string;
    normalized_message: string;
    translated_message?: string | null;
    actions: MascotAction[];
    artifacts: Array<Record<string, unknown>>;
    navigation?: { href?: string; target?: string; notebook_id?: string } | null;
    requires_confirmation: boolean;
    confirmation_id?: string | null;
    follow_up_suggestions: string[];
    notebook_id?: string | null;
    trace_id: string;
};

export type MascotChatMessage = {
    id: string;
    role: "user" | "assistant";
    text: string;
    response?: MascotResponse | null;
};
