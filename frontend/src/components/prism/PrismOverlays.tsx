"use client";

import { cn } from "@/lib/utils";

export function PrismOverlay({
    className,
    children,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("prism-overlay", className)} {...props}>
            {children}
        </div>
    );
}

export function PrismDialog({
    className,
    children,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("prism-dialog", className)} {...props}>
            {children}
        </div>
    );
}

export function PrismDrawer({
    className,
    children,
    ...props
}: React.HTMLAttributes<HTMLElement>) {
    return (
        <aside className={cn("prism-drawer", className)} {...props}>
            {children}
        </aside>
    );
}

export function PrismDialogHeader({
    className,
    children,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("prism-dialog-header", className)} {...props}>
            {children}
        </div>
    );
}

export function PrismDialogFooter({
    className,
    children,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={cn("prism-dialog-footer", className)} {...props}>
            {children}
        </div>
    );
}
