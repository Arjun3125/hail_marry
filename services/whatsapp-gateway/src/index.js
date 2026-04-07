/**
 * VidyaOS WhatsApp Gateway — High-Load Node.js Microservice
 *
 * Responsibilities:
 *  1. Receive Meta Cloud API webhooks (GET verify + POST inbound)
 *  2. Validate HMAC-SHA256 signatures
 *  3. Normalize payloads and deduplicate messages via Redis
 *  4. Enqueue normalized messages onto a BullMQ queue
 *  5. Worker drains queue → forwards to Python backend bridge endpoint
 *  6. Health-check endpoint for Docker / Kubernetes probes
 *
 * This service is designed to handle thousands of concurrent connections
 * and return 200 OK to Meta within milliseconds, while the actual AI
 * processing happens asynchronously in the Python backend.
 */

const express = require("express");
const crypto = require("crypto");
const helmet = require("helmet");
const rateLimit = require("express-rate-limit");
const { createLogger } = require("./logger");
const { createQueue, createWorker } = require("./queue");
const { createHealthRouter } = require("./health");

const logger = createLogger("gateway");

// ─── Configuration ──────────────────────────────────────────
const PORT = parseInt(process.env.WA_GATEWAY_PORT || "3100", 10);
const VERIFY_TOKEN = process.env.WHATSAPP_VERIFY_TOKEN || "vidyaos-wa-verify";
const APP_SECRET = process.env.WHATSAPP_APP_SECRET || "";
const PYTHON_BACKEND_URL =
  process.env.PYTHON_BACKEND_URL || "http://localhost:7125";
const BRIDGE_PATH =
  process.env.BRIDGE_PATH || "/api/whatsapp/bridge/inbound";
const REDIS_URL = process.env.REDIS_URL || "redis://localhost:6379";
const DEDUP_TTL_SECONDS = parseInt(process.env.DEDUP_TTL || "3600", 10);

// ─── Express App ────────────────────────────────────────────
const app = express();

// Security
app.use(helmet());
app.use(
  rateLimit({
    windowMs: 60_000,
    max: parseInt(process.env.WA_GATEWAY_RATE_LIMIT || "500", 10),
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: "Too many requests" },
  })
);

// We need raw body for HMAC verification
app.use(
  express.json({
    verify: (req, _res, buf) => {
      req.rawBody = buf;
    },
  })
);

// ─── Redis (for dedup) ──────────────────────────────────────
let redis = null;
try {
  const Redis = require("ioredis");
  redis = new Redis(REDIS_URL, { maxRetriesPerRequest: 1, lazyConnect: true });
  redis.connect().catch((err) => {
    logger.warn({ err }, "Redis connection failed — dedup disabled");
    redis = null;
  });
} catch (err) {
  logger.warn("ioredis not available — dedup disabled");
}

// ─── BullMQ Queue ───────────────────────────────────────────
const { queue, worker } = (() => {
  try {
    return createQueue({
      redisUrl: REDIS_URL,
      backendUrl: `${PYTHON_BACKEND_URL}${BRIDGE_PATH}`,
      logger,
    });
  } catch (err) {
    logger.warn({ err }, "BullMQ unavailable — will forward synchronously");
    return { queue: null, worker: null };
  }
})();

// ─── HMAC Signature Verification ────────────────────────────
function verifySignature(rawBody, signature) {
  if (!APP_SECRET) {
    logger.warn("WHATSAPP_APP_SECRET not set — skipping signature check");
    return true;
  }
  if (!signature) return false;
  const expected =
    "sha256=" +
    crypto.createHmac("sha256", APP_SECRET).update(rawBody).digest("hex");
  return crypto.timingSafeEqual(
    Buffer.from(expected),
    Buffer.from(signature)
  );
}

// ─── Message Deduplication ──────────────────────────────────
async function isDuplicate(messageId) {
  if (!redis || !messageId) return false;
  try {
    const key = `wa_gw:dedup:${messageId}`;
    const exists = await redis.get(key);
    if (exists) return true;
    await redis.setex(key, DEDUP_TTL_SECONDS, "1");
    return false;
  } catch {
    return false;
  }
}

// ─── Extract Messages from Meta Payload ─────────────────────
function extractMessages(payload) {
  const messages = [];
  for (const entry of payload.entry || []) {
    for (const change of entry.changes || []) {
      const value = change.value || {};
      for (const msg of value.messages || []) {
        const base = {
          phone: msg.from || "",
          wa_message_id: msg.id || "",
          timestamp: msg.timestamp,
        };

        if (msg.type === "text") {
          messages.push({
            ...base,
            text: msg.text?.body || "",
            message_type: "text",
          });
        } else if (msg.type === "interactive") {
          const reply =
            msg.interactive?.button_reply || msg.interactive?.list_reply || {};
          messages.push({
            ...base,
            text: reply.id || reply.title || "",
            message_type: "interactive",
          });
        } else if (["document", "image", "video", "audio"].includes(msg.type)) {
          const media = msg[msg.type] || {};
          messages.push({
            ...base,
            text: media.caption || "",
            message_type: msg.type,
            media_id: media.id || null,
            media_filename: media.filename || null,
            media_mime_type: media.mime_type || null,
          });
        }
      }
    }
  }
  return messages;
}

// ─── Routes ─────────────────────────────────────────────────

// Webhook verification (GET)
app.get("/webhook", (req, res) => {
  const mode = req.query["hub.mode"];
  const token = req.query["hub.verify_token"];
  const challenge = req.query["hub.challenge"];

  if (mode === "subscribe" && token === VERIFY_TOKEN) {
    logger.info("Webhook verified successfully");
    return res.status(200).send(challenge);
  }
  return res.status(403).json({ error: "Verification failed" });
});

// Inbound webhook (POST)
app.post("/webhook", async (req, res) => {
  // Verify signature
  const signature = req.headers["x-hub-signature-256"] || "";
  if (!verifySignature(req.rawBody, signature)) {
    logger.warn("Invalid webhook signature");
    return res.status(403).json({ error: "Invalid signature" });
  }

  // Must respond 200 to Meta immediately
  res.status(200).json({ status: "ok" });

  // Extract and process messages
  const messages = extractMessages(req.body);
  for (const msg of messages) {
    if (!msg.phone || (!msg.text && !msg.media_id)) continue;

    const dup = await isDuplicate(msg.wa_message_id);
    if (dup) {
      logger.debug({ wa_id: msg.wa_message_id }, "Duplicate message skipped");
      continue;
    }

    // Enqueue for async processing
    if (queue) {
      try {
        await queue.add("inbound_message", msg, {
          attempts: 3,
          backoff: { type: "exponential", delay: 2000 },
          removeOnComplete: 1000,
          removeOnFail: 5000,
        });
        logger.info({ phone: msg.phone }, "Message enqueued");
      } catch (err) {
        logger.error({ err, phone: msg.phone }, "Queue add failed — forwarding sync");
        await forwardSync(msg);
      }
    } else {
      await forwardSync(msg);
    }
  }
});

// Synchronous fallback when BullMQ is unavailable
async function forwardSync(msg) {
  try {
    const axios = require("axios");
    await axios.post(`${PYTHON_BACKEND_URL}${BRIDGE_PATH}`, msg, {
      timeout: 30_000,
      headers: { "X-Internal-Gateway": "vidyaos-wa-gw" },
    });
  } catch (err) {
    logger.error({ err, phone: msg.phone }, "Sync forward failed");
  }
}

// Health
app.use("/health", createHealthRouter({ redis, queue }));

// ─── Startup ────────────────────────────────────────────────
// Export for testing
module.exports = { app, extractMessages, verifySignature };

if (require.main === module) {
  app.listen(PORT, () => {
    logger.info({ port: PORT }, "WhatsApp Gateway started");
  });
}
