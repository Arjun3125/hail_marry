/**
 * Health-check and readiness probe router.
 */
const express = require("express");

function createHealthRouter({ redis, queue }) {
  const router = express.Router();

  router.get("/", async (_req, res) => {
    const checks = {
      status: "ok",
      uptime_seconds: Math.floor(process.uptime()),
      redis: "unknown",
      queue: "unknown",
    };

    // Redis check
    if (redis) {
      try {
        await redis.ping();
        checks.redis = "connected";
      } catch {
        checks.redis = "disconnected";
      }
    } else {
      checks.redis = "disabled";
    }

    // Queue check
    if (queue) {
      try {
        const waiting = await queue.getWaitingCount();
        const active = await queue.getActiveCount();
        checks.queue = "connected";
        checks.queue_waiting = waiting;
        checks.queue_active = active;
      } catch {
        checks.queue = "disconnected";
      }
    } else {
      checks.queue = "disabled";
    }

    const isHealthy =
      checks.redis !== "disconnected" && checks.queue !== "disconnected";
    res.status(isHealthy ? 200 : 503).json(checks);
  });

  router.get("/ready", async (_req, res) => {
    // Readiness: can we accept traffic?
    if (redis) {
      try {
        await redis.ping();
      } catch {
        return res.status(503).json({ ready: false, reason: "redis" });
      }
    }
    res.json({ ready: true });
  });

  return router;
}

module.exports = { createHealthRouter };
