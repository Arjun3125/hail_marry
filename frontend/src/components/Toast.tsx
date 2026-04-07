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
    success: <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-emerald-300" />,
    error: <XCircle className="h-4 w-4 flex-shrink-0 text-rose-300" />,
    warning: <AlertTriangle className="h-4 w-4 flex-shrink-0 text-amber-200" />,
    info: <Info className="h-4 w-4 flex-shrink-0 text-sky-200" />,
};

const bgColors = {
    success: "prism-toast prism-toast-success",
    error: "prism-toast prism-toast-error",
    warning: "prism-toast prism-toast-warning",
    info: "prism-toast prism-toast-info",
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
            <div className="pointer-events-none fixed right-4 top-4 z-[100] flex w-full max-w-sm flex-col gap-2">
                {toasts.map((t) => (
                    <div
                        key={t.id}
                        className={`pointer-events-auto flex items-start gap-3 px-4 py-3 text-sm font-medium animate-[slideIn_0.25s_ease-out] ${bgColors[t.type]}`}
                    >
                        {icons[t.type]}
                        <span className="flex-1 leading-6">{t.message}</span>
                        <button
                            onClick={() => removeToast(t.id)}
                            className="mt-0.5 text-current opacity-45 transition-opacity hover:opacity-80"
                        >
                            <X className="w-3.5 h-3.5" />
                        </button>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
}
