# VidyaOS Offensive Security Audit Report

## Audit Overview
A comprehensive, line-by-line offensive security audit was conducted against the VidyaOS codebase. The analysis focused on backend logic, authentication flows, middleware chains, input sanitization, API routing, and configuration management. 

Our adversarial assessment assumes the mindset of both sophisticated red-team actors and opportunistic script kiddies. The findings below detail every identified vulnerability vector that could allow an attacker to leverage the system.

*(Note: Per the engagement rules of engagement constraints, no source code modification has been made. This report strictly analyzes and discloses vulnerabilities.)*

---

## 🚨 Critical Severity

### 1. Authentication Bypass & Privilege Escalation (`DEMO_MODE`)
**Location:** `backend/auth/dependencies.py` > `get_current_user` and `is_demo_mode`
**Vulnerability:** 
The application implements a "Demo Mode" that acts as a hardcoded backdoor, allowing authentication bypass using simple HTTP headers (`X-Demo-Role`) or cookies. Currently, the fallback mechanism checks if `app_env != "production"`.
**Exploitation Scenario:**
If a misconfiguration occurs in production (e.g., `APP_ENV` is mistyped or missing), an external attacker can pass an `X-Demo-Role: admin` header and completely seize administrative control over the application without possessing valid credentials.
**Remediation:** 
Remove demo/backdoor logic entirely from the core production authentication paths (`dependencies.py`). Demo modes should be strictly isolated to completely separate launch artifacts, never deployed via runtime toggles.

### 2. Hardcoded Secrets Identification
**Location:** Root `.env` and `docker-compose.yml`
**Vulnerability:**
Active, sensitive external API keys (including NVIDIA `OPENAI_API_KEY` and `EMBEDDING_API_KEY`), as well as default database passwords, have been hardcoded directly into the repository files.
**Exploitation Scenario:**
An attacker gaining read access to the repository (either via insider threat, accidental public exposure, or LFI vulnerabilities) can immediately hijack downstream billable API quotas or access databases.
**Remediation:** 
Immediately revoke and rotate all exposed keys. Utilize a secrets management provider (e.g., AWS Secrets Manager, HashiCorp Vault) and inject secrets exclusively via local environment variables outside the repository.

---

## 🔴 High Severity

### 3. Server-Side Request Forgery (SSRF)
**Location:** `backend/src/domains/identity/services/saml_sso.py` > `import_tenant_saml_metadata`
**Vulnerability:**
The SAML upload interface allows importing metadata from a remote URL via the `metadata_url` field. The backend calls `httpx.AsyncClient().get(metadata_url)` with **no URL sanitization or protocol/IP restriction**.
**Exploitation Scenario:**
An attacker (who obtained Admin access via the `DEMO_MODE` vulnerability or via compromised credentials) can provide a payload like `http://169.254.169.254/latest/meta-data/` to compromise the internal AWS instance metadata service, or scan the internal private VPC network of the backend infrastructure.
**Remediation:**
Implement a strict URL parser that rejects loopback addresses (`127.0.0.1`), local network spaces (e.g., `10.x.x.x`, `192.168.x.x`), and known metadata endpoints (`169.254.169.254`). 

### 4. Denial of Service (DoS) via Memory Exhaustion (Rate Limit Fallback)
**Location:** `backend/middleware/rate_limit.py`
**Vulnerability:**
The `RateLimitMiddleware` relies on Redis to track IP requests. If Redis goes offline or connection fails, the middleware falls back to an unbounded, global, in-memory dictionary (`_memory_store`).
**Exploitation Scenario:**
An attacker detecting a Redis configuration failure can launch an intentional, sustained distributed request barrage utilizing random spoofed IPs. The global dictionary will infinitely store request counters in server memory, rapidly triggering an Out-of-Memory (OOM) crash that takes down the entire application container.
**Remediation:**
Utilize an explicitly bounded cache (e.g., `cachetools.LRUCache`) for the in-memory fallback, or fail securely and limit all fallback states to strict default drops in production.

---

## 🟠 Medium Severity

### 5. CORS/CSRF Attack Surface Expansion
**Location:** `backend/middleware/csrf.py` and `config.py`
**Vulnerability:**
The permissive Cross-Origin allow-list dynamically includes `*.vercel.app` domains when `debug` mode is `True` (and the codebase has risky defaults where debugging can easily enable itself via missing environment checks).
**Exploitation Scenario:**
If `debug` is accidentally enabled in production, an attacker could host a malicious Vercel deployment and force a victim's browser to execute unauthorized state-changing requests against the backend (classic CSRF execution).
**Remediation:**
Eliminate wildcard subdomains in CORS and strictly enforce the `Origin` checks to known, explicitly registered frontend production endpoints. Debug configurations must never loosen cross-origin protections.

### 6. Command Argument Injection (Options Injection)
**Location:** `backend/src/infrastructure/vector_store/ingestion.py` > `extract_media_transcript`
**Vulnerability:**
The media processing pipeline invokes `subprocess.run(["ffmpeg", "-y", "-i", file_path, ...])`. 
**Exploitation Scenario:**
If another module invokes this pipeline by supplying a raw `file_path` that begins with a hyphen (`-`), FFmpeg will interpret the filename as a command-line option rather than a path. While currently mitigated via UUID-prefixing in the Mascot upload component, secondary API interactions or developers calling this function could accidentally introduce OS-level option injection vulnerabilities reading arbitrary system files into the transcription.
**Remediation:**
Prepend `file_path` with `./` or resolve paths absolutely with `Path(file_path).resolve()` to ensure it is never parsed as a flag by `ffmpeg`.

### 7. Weak Cryptographic Practices (JWT Token Generation)
**Location:** `backend/auth/jwt.py`
**Vulnerability:**
The module generates refresh tokens by concatenating `_refresh` to the primary configuration secret key. 
**Exploitation Scenario:**
Using directly derived secrets for separate token layers violates cryptographic compartmentalization. If an attacker discovers the logic, cracking the refresh signature reveals the primary access key signature and vice versa. 
**Remediation:**
Define an explicitly independent `REFRESH_SECRET_KEY` in environment variables. Do not computationally tie separate security contexts to a singular secret root within standard app logic.

---

## 🔵 Low Severity / Defense in Depth Deficiencies

### 8. Fail-Open CAPTCHA Implementation
**Location:** `backend/middleware/captcha.py`
**Vulnerability:**
The reCAPTCHA validation dependency implements a bypass `return True` silently if the reCAPTCHA secret key is absent in the environment variables.
**Exploitation Scenario:**
A devops configuration oversight results in missing captcha keys. Instead of breaking deployment alerting the team, the application silently permits automated bots to hit all rate-limit-protected administrative interfaces simultaneously.
**Remediation:**
The application should refuse to start or hard-block those endpoints (`HTTP 500`) to fail-securely if security configuration primitives are missing. 

### 9. Potential Path Traversal from Database Poisoning
**Location:** `backend/src/interfaces/rest_api/ai/routes/documents.py` > `view_document`
**Vulnerability:**
The endpoint reads files by extracting `doc.storage_path` from the PostgreSQL database and piping it directly to `FileResponse`.
**Exploitation Scenario:**
If a separate (or future) SQL Injection or ORM bypass vulnerability allows an attacker to manipulate `doc.storage_path` inside the database, they can point the path to `/etc/shadow` or `.env` and retrieve those files. 
**Remediation:**
Even though the database is assumed trusted, validate that `file_path.resolve()` securely resides within `STORAGE_ROOT` (`ensure_storage_dir`) before emitting the file response.
