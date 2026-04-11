/**
 * useWebSocket - Custom React hook for real-time WebSocket connection
 */

import { useCallback, useEffect, useRef, useState } from "react";

type JsonMap = Record<string, unknown>;

type WebSocketEvent = {
    event: string;
    timestamp: string;
    data: JsonMap;
};

type EventListener = (data: unknown) => void;

interface UseWebSocketOptions {
    onConnect?: () => void;
    onDisconnect?: () => void;
    onError?: (error: Error) => void;
    reconnectInterval?: number;
    maxReconnectAttempts?: number;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
    const {
        onConnect,
        onDisconnect,
        onError,
        reconnectInterval = 3000,
        maxReconnectAttempts = 5,
    } = options;

    const [isConnected, setIsConnected] = useState(false);
    const [reconnectAttempts, setReconnectAttempts] = useState(0);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
    const eventListenersRef = useRef<Map<string, Set<EventListener>>>(new Map());

    const stopHeartbeat = useCallback(() => {
        if (heartbeatIntervalRef.current) {
            clearInterval(heartbeatIntervalRef.current);
            heartbeatIntervalRef.current = null;
        }
    }, []);

    const startHeartbeat = useCallback(() => {
        stopHeartbeat();
        heartbeatIntervalRef.current = setInterval(() => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send("ping");
            }
        }, 30000);
    }, [stopHeartbeat]);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        try {
            const token = localStorage.getItem("auth_token");
            if (!token) {
                throw new Error("No authentication token found");
            }

            const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
            const url = `${protocol}//${window.location.host}/ws/realtime?token=${token}`;
            const ws = new WebSocket(url);

            ws.onopen = () => {
                logger.info("WebSocket connected");
                setIsConnected(true);
                setReconnectAttempts(0);
                onConnect?.();
                startHeartbeat();
            };

            ws.onmessage = (event) => {
                if (event.data === "pong") {
                    logger.debug("Heartbeat pong received");
                    return;
                }

                try {
                    const message = JSON.parse(event.data as string) as WebSocketEvent;

                    if (message.event === "connection.established") {
                        logger.debug("Connection established", message.data);
                        return;
                    }

                    const listeners = eventListenersRef.current.get(message.event);
                    listeners?.forEach((listener) => {
                        try {
                            listener(message.data);
                        } catch (err) {
                            logger.error(`Error in listener for ${message.event}:`, err);
                        }
                    });

                    const anyListeners = eventListenersRef.current.get("*");
                    anyListeners?.forEach((listener) => {
                        try {
                            listener(message);
                        } catch (err) {
                            logger.error("Error in universal listener:", err);
                        }
                    });
                } catch (err) {
                    logger.error("Error parsing WebSocket message:", err);
                }
            };

            ws.onerror = (error) => {
                logger.error("WebSocket error:", error);
                onError?.(new Error("WebSocket error"));
            };

            ws.onclose = () => {
                logger.info("WebSocket disconnected");
                setIsConnected(false);
                stopHeartbeat();
                onDisconnect?.();

                if (reconnectAttempts < maxReconnectAttempts) {
                    const nextAttempt = reconnectAttempts + 1;
                    setReconnectAttempts(nextAttempt);
                    logger.info(
                        `Attempting to reconnect (${nextAttempt}/${maxReconnectAttempts}) in ${reconnectInterval}ms`,
                    );
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, reconnectInterval);
                } else {
                    logger.error("Max reconnection attempts reached");
                    onError?.(new Error("Max reconnection attempts reached"));
                }
            };

            wsRef.current = ws;
        } catch (err) {
            logger.error("Failed to create WebSocket:", err);
            onError?.(err instanceof Error ? err : new Error(String(err)));
        }
    }, [
        maxReconnectAttempts,
        onConnect,
        onDisconnect,
        onError,
        reconnectAttempts,
        reconnectInterval,
        startHeartbeat,
        stopHeartbeat,
    ]);

    const on = useCallback((event: string, listener: EventListener) => {
        if (!eventListenersRef.current.has(event)) {
            eventListenersRef.current.set(event, new Set());
        }
        eventListenersRef.current.get(event)?.add(listener);

        return () => {
            const listeners = eventListenersRef.current.get(event);
            if (!listeners) return;
            listeners.delete(listener);
            if (listeners.size === 0) {
                eventListenersRef.current.delete(event);
            }
        };
    }, []);

    const off = useCallback((event: string, listener: EventListener) => {
        const listeners = eventListenersRef.current.get(event);
        if (!listeners) return;
        listeners.delete(listener);
        if (listeners.size === 0) {
            eventListenersRef.current.delete(event);
        }
    }, []);

    const send = useCallback((data: JsonMap) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
        } else {
            logger.warn("WebSocket is not connected, message not sent");
        }
    }, []);

    useEffect(() => {
        connect();

        return () => {
            stopHeartbeat();
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.close();
            }
        };
    }, [connect, stopHeartbeat]);

    return {
        isConnected,
        on,
        off,
        send,
        reconnectAttempts,
    };
};

const logger = {
    debug: (msg: string, data?: unknown) => {
        if (process.env.NODE_ENV === "development") {
            console.debug(`[WebSocket] ${msg}`, data);
        }
    },
    info: (msg: string, data?: unknown) => {
        console.info(`[WebSocket] ${msg}`, data);
    },
    warn: (msg: string, data?: unknown) => {
        console.warn(`[WebSocket] ${msg}`, data);
    },
    error: (msg: string, data?: unknown) => {
        console.error(`[WebSocket] ${msg}`, data);
    },
};
