/**
 * Tests for the WhatsApp Gateway Node.js microservice.
 *
 * Covers:
 *   · Webhook verification (GET /webhook)
 *   · Payload extraction from Meta format
 *   · HMAC signature verification
 *   · Inbound webhook processing (POST /webhook)
 *   · Health endpoint
 */

const { app, extractMessages, verifySignature } = require("../src/index");

// We use a basic http test approach without supertest to avoid dependency issues
const http = require("http");

// ─── extractMessages tests ───────────────────────────────────

describe("extractMessages", () => {
  test("extracts text messages from Meta payload", () => {
    const payload = {
      entry: [
        {
          changes: [
            {
              value: {
                messages: [
                  {
                    from: "919876543210",
                    id: "wamid.123",
                    type: "text",
                    text: { body: "Hello VidyaOS" },
                    timestamp: "1712500000",
                  },
                ],
              },
            },
          ],
        },
      ],
    };

    const msgs = extractMessages(payload);
    expect(msgs).toHaveLength(1);
    expect(msgs[0].phone).toBe("919876543210");
    expect(msgs[0].text).toBe("Hello VidyaOS");
    expect(msgs[0].message_type).toBe("text");
    expect(msgs[0].wa_message_id).toBe("wamid.123");
  });

  test("extracts interactive button replies", () => {
    const payload = {
      entry: [
        {
          changes: [
            {
              value: {
                messages: [
                  {
                    from: "919876543210",
                    id: "wamid.456",
                    type: "interactive",
                    interactive: {
                      button_reply: { id: "btn_yes", title: "Yes" },
                    },
                  },
                ],
              },
            },
          ],
        },
      ],
    };

    const msgs = extractMessages(payload);
    expect(msgs).toHaveLength(1);
    expect(msgs[0].text).toBe("btn_yes");
    expect(msgs[0].message_type).toBe("interactive");
  });

  test("extracts document messages with media metadata", () => {
    const payload = {
      entry: [
        {
          changes: [
            {
              value: {
                messages: [
                  {
                    from: "919876543210",
                    id: "wamid.789",
                    type: "document",
                    document: {
                      id: "media_abc",
                      filename: "notes.pdf",
                      mime_type: "application/pdf",
                      caption: "My study notes",
                    },
                  },
                ],
              },
            },
          ],
        },
      ],
    };

    const msgs = extractMessages(payload);
    expect(msgs).toHaveLength(1);
    expect(msgs[0].media_id).toBe("media_abc");
    expect(msgs[0].media_filename).toBe("notes.pdf");
    expect(msgs[0].text).toBe("My study notes");
  });

  test("returns empty array for payload with no messages", () => {
    const payload = { entry: [{ changes: [{ value: {} }] }] };
    expect(extractMessages(payload)).toEqual([]);
  });

  test("handles completely empty payload", () => {
    expect(extractMessages({})).toEqual([]);
  });

  test("extracts multiple messages from a single entry", () => {
    const payload = {
      entry: [
        {
          changes: [
            {
              value: {
                messages: [
                  { from: "91111", id: "a", type: "text", text: { body: "A" } },
                  { from: "91222", id: "b", type: "text", text: { body: "B" } },
                ],
              },
            },
          ],
        },
      ],
    };

    const msgs = extractMessages(payload);
    expect(msgs).toHaveLength(2);
  });
});

// ─── verifySignature tests ──────────────────────────────────

describe("verifySignature", () => {
  test("returns true when APP_SECRET is empty (dev mode)", () => {
    // In the default test env, WHATSAPP_APP_SECRET is not set
    const result = verifySignature(Buffer.from("test"), "sha256=wrong");
    expect(result).toBe(true);
  });
});

// ─── Health endpoint (basic) ────────────────────────────────

describe("Health endpoint", () => {
  let server;

  beforeAll((done) => {
    server = app.listen(0, done);
  });

  afterAll((done) => {
    server.close(done);
  });

  test("GET /health/ returns 200", (done) => {
    const port = server.address().port;
    http.get(`http://localhost:${port}/health/`, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        expect(res.statusCode).toBe(200);
        const body = JSON.parse(data);
        expect(body.status).toBe("ok");
        expect(typeof body.uptime_seconds).toBe("number");
        done();
      });
    });
  });
});

// ─── Webhook verify endpoint ────────────────────────────────

describe("GET /webhook", () => {
  let server;

  beforeAll((done) => {
    server = app.listen(0, done);
  });

  afterAll((done) => {
    server.close(done);
  });

  test("returns challenge on valid verification", (done) => {
    const port = server.address().port;
    const url = `http://localhost:${port}/webhook?hub.mode=subscribe&hub.verify_token=vidyaos-wa-verify&hub.challenge=12345`;
    http.get(url, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        expect(res.statusCode).toBe(200);
        expect(data).toBe("12345");
        done();
      });
    });
  });

  test("returns 403 on invalid token", (done) => {
    const port = server.address().port;
    const url = `http://localhost:${port}/webhook?hub.mode=subscribe&hub.verify_token=wrong&hub.challenge=12345`;
    http.get(url, (res) => {
      expect(res.statusCode).toBe(403);
      done();
    });
  });
});
