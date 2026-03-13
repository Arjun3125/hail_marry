"use client";

import { createContext, useContext, useState, useCallback, useRef } from "react";
import { CheckCircle2, AlertTriangle, Info, X, XCircle } from "lucide-react";

type ToastType = "success" | "error" | "info" | "warning";

interface Toast {
    id: number;
    type: ToastType;
    message: string;
}

interface ToastContextType {
    toast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType>({
    toast: () => { },
});

export const useToast = () => useContext(ToastContext);

const icons = {
    success: <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />,
    error: <XCircle className="w-4 h-4 text-red-500 flex-shrink-0" />,
    warning: <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0" />,
    info: <Info className="w-4 h-4 text-blue-500 flex-shrink-0" />,
};

const bgColors = {
    success: "bg-emerald-50 border-emerald-200 text-emerald-800",
    error: "bg-error-subtle border-error-subtle text-status-red",
    warning: "bg-warning-subtle border-warning-subtle text-status-amber",
    info: "bg-info-subtle border-blue-200 text-status-blue",
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
    const [toasts, setToasts] = useState<Toast[]>([]);
    const idRef = useRef(0);

    const addToast = useCallback((message: string, type: ToastType = "info") => {
        const id = ++idRef.current;
        setToasts((prev) => [...prev, { id, type, message }]);
        setTimeout(() => {
            setToasts((prev) => prev.filter((t) => t.id !== id));
        }, 3500);
    }, []);

    const removeToast = useCallback((id: number) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    return (
        <ToastContext.Provider value={{ toast: addToast }}>
            {children}
            {/* Toast container */}
            <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
                {toasts.map((t) => (
                    <div
                        key={t.id}
                        className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg text-sm font-medium animate-[slideIn_0.25s_ease-out] ${bgColors[t.type]}`}
                    >
                        {icons[t.type]}
                        <span className="flex-1">{t.message}</span>
                        <button
                            onClick={() => removeToast(t.id)}
                            className="text-current opacity-40 hover:opacity-70 transition-opacity"
                        >
                            <X className="w-3.5 h-3.5" />
                        </button>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
}
