"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ReactNode } from "react";

interface AnimatedPageProps {
    children: ReactNode;
    className?: string;
}

export function AnimatedPage({ children, className }: AnimatedPageProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

interface AnimatedCardProps {
    children: ReactNode;
    className?: string;
    delay?: number;
}

export function AnimatedCard({ children, className, delay = 0 }: AnimatedCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay, ease: "easeOut" }}
            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

interface AnimatedListProps {
    children: ReactNode[];
    className?: string;
    staggerDelay?: number;
}

export function AnimatedList({ children, className, staggerDelay = 0.1 }: AnimatedListProps) {
    return (
        <div className={className}>
            <AnimatePresence mode="wait">
                {children.map((child, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ duration: 0.3, delay: index * staggerDelay }}
                    >
                        {child}
                    </motion.div>
                ))}
            </AnimatePresence>
        </div>
    );
}

interface FadeInProps {
    children: ReactNode;
    className?: string;
    delay?: number;
}

export function FadeIn({ children, className, delay = 0 }: FadeInProps) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3, delay }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

interface SlideInProps {
    children: ReactNode;
    className?: string;
    direction?: "left" | "right" | "up" | "down";
    delay?: number;
}

export function SlideIn({ children, className, direction = "left", delay = 0 }: SlideInProps) {
    const directions = {
        left: { x: -20, y: 0 },
        right: { x: 20, y: 0 },
        up: { x: 0, y: -20 },
        down: { x: 0, y: 20 },
    };

    return (
        <motion.div
            initial={{ opacity: 0, ...directions[direction] }}
            animate={{ opacity: 1, x: 0, y: 0 }}
            transition={{ duration: 0.4, delay, ease: "easeOut" }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

// Tool switching animation wrapper
interface ToolTransitionProps {
    children: ReactNode;
    toolId: string;
}

export function ToolTransition({ children, toolId }: ToolTransitionProps) {
    return (
        <AnimatePresence mode="wait">
            <motion.div
                key={toolId}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
            >
                {children}
            </motion.div>
        </AnimatePresence>
    );
}

// Loading pulse animation
export function LoadingPulse({ className }: { className?: string }) {
    return (
        <motion.div
            className={className}
            animate={{
                scale: [1, 1.1, 1],
                opacity: [0.5, 1, 0.5],
            }}
            transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut",
            }}
        />
    );
}

// Stagger container for lists
interface StaggerContainerProps {
    children: ReactNode;
    className?: string;
    staggerDelay?: number;
}

export function StaggerContainer({ children, className, staggerDelay = 0.1 }: StaggerContainerProps) {
    return (
        <motion.div
            initial="hidden"
            animate="visible"
            variants={{
                hidden: { opacity: 0 },
                visible: {
                    opacity: 1,
                    transition: {
                        staggerChildren: staggerDelay,
                    },
                },
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

// Stagger item for use inside StaggerContainer
interface StaggerItemProps {
    children: ReactNode;
    className?: string;
}

export function StaggerItem({ children, className }: StaggerItemProps) {
    return (
        <motion.div
            variants={{
                hidden: { opacity: 0, y: 20 },
                visible: { opacity: 1, y: 0 },
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}
