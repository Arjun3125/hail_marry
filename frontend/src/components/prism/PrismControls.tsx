"use client";

import { Search } from "lucide-react";

import { cn } from "@/lib/utils";

export function PrismToolbar({
    className,
    children,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("prism-toolbar", className)} {...props}>
            {children}
        </div>
    );
}

export function PrismSearchField({
    className,
    inputClassName,
    ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
    inputClassName?: string;
}) {
    return (
        <label className={cn("prism-search", className)}>
            <Search className="h-4 w-4 shrink-0 text-[var(--text-muted)]" />
            <input className={cn(inputClassName)} {...props} />
        </label>
    );
}

export function PrismSelect({
    className,
    children,
    ...props
}: React.SelectHTMLAttributes<HTMLSelectElement>) {
    return (
        <select className={cn("prism-select", className)} {...props}>
            {children}
        </select>
    );
}

export function PrismInput({
    className,
    ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
    return <input className={cn("prism-input", className)} {...props} />;
}

export function PrismTextarea({
    className,
    ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
    return <textarea className={cn("prism-textarea", className)} {...props} />;
}

export function PrismTabList({
    className,
    children,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("flex flex-wrap gap-2", className)} {...props}>
            {children}
        </div>
    );
}

export function PrismTabButton({
    active = false,
    className,
    children,
    ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
    active?: boolean;
}) {
    return (
        <button
            data-active={active ? "true" : "false"}
            className={cn("prism-tab", className)}
            {...props}
        >
            {children}
        </button>
    );
}

export function PrismTableShell({
    className,
    children,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("table-responsive prism-table-shell", className)} {...props}>
            {children}
        </div>
    );
}

export function PrismPagination({
    className,
    children,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("flex items-center justify-center gap-3", className)} {...props}>
            {children}
        </div>
    );
}

export function PrismPaginationButton({
    className,
    children,
    ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
    return (
        <button className={cn("prism-action-secondary text-sm", className)} {...props}>
            {children}
        </button>
    );
}
