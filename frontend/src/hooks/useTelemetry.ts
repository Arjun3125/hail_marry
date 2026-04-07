import { useCallback } from "react";

export interface TelemetryPayload {
  eventName: string;
  eventFamily?: "business" | "educational" | "operational";
  surface?: string;
  target?: string;
  channel?: string;
  value?: number;
  metadata?: Record<string, unknown>;
}

export function useTelemetry() {
  const record = useCallback(async (payload: TelemetryPayload) => {
    try {
      const response = await fetch("/api/platform/telemetry/event", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        console.warn("Telemetry emission failed:", response.statusText);
      }
    } catch (error) {
      console.error("Telemetry error:", error);
    }
  }, []);

  return { record };
}
