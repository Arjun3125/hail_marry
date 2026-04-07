/**
 * Structured logger using pino.
 */

function createLogger(name) {
  try {
    const pino = require("pino");
    return pino({
      name,
      level: process.env.LOG_LEVEL || "info",
      transport:
        process.env.NODE_ENV !== "production"
          ? { target: "pino-pretty", options: { colorize: true } }
          : undefined,
    });
  } catch {
    // Fallback to console
    return {
      info: (...args) => console.log(`[${name}]`, ...args),
      warn: (...args) => console.warn(`[${name}]`, ...args),
      error: (...args) => console.error(`[${name}]`, ...args),
      debug: (...args) => console.debug(`[${name}]`, ...args),
    };
  }
}

module.exports = { createLogger };
