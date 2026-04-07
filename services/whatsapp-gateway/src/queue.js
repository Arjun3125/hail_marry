/**
 * BullMQ queue + worker for forwarding normalized WhatsApp messages
 * to the Python backend's bridge endpoint.
 */

function createQueue({ redisUrl, backendUrl, logger }) {
  const { Queue, Worker } = require("bullmq");
  const axios = require("axios");
  const IORedis = require("ioredis");

  const connection = new IORedis(redisUrl, { maxRetriesPerRequest: null });

  const queue = new Queue("wa-inbound", { connection });

  const worker = new Worker(
    "wa-inbound",
    async (job) => {
      const msg = job.data;
      const startMs = Date.now();
      try {
        const resp = await axios.post(backendUrl, msg, {
          timeout: 60_000,
          headers: {
            "Content-Type": "application/json",
            "X-Internal-Gateway": "vidyaos-wa-gw",
          },
        });
        const elapsed = Date.now() - startMs;
        logger.info(
          { phone: msg.phone, elapsed_ms: elapsed, status: resp.status },
          "Forwarded to backend"
        );
        return { status: resp.status, elapsed_ms: elapsed };
      } catch (err) {
        const elapsed = Date.now() - startMs;
        logger.error(
          { err: err.message, phone: msg.phone, elapsed_ms: elapsed },
          "Forward to backend failed"
        );
        throw err; // BullMQ will retry based on job config
      }
    },
    {
      connection,
      concurrency: parseInt(process.env.WA_WORKER_CONCURRENCY || "10", 10),
    }
  );

  worker.on("completed", (job) => {
    logger.debug({ jobId: job.id }, "Job completed");
  });

  worker.on("failed", (job, err) => {
    logger.warn(
      { jobId: job?.id, err: err.message, attempts: job?.attemptsMade },
      "Job failed"
    );
  });

  return { queue, worker };
}

module.exports = { createQueue };
