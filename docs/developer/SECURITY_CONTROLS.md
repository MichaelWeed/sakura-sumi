# Sakura Sumi Security Controls Documentation

This document describes the security architecture, threat mitigations, and configuration parameters implemented in **Sakura Sumi - Visual Token Arbitrage Engine** to protect end-users and codebase data.

---

## 1. Threat Mitigation Controls

### CSRF Protection (Same-Origin & Referer Validation)
To protect local users running the web portal, all state-changing API endpoints (`POST` requests) are secured against Cross-Site Request Forgery (CSRF).
* **Mechanism**: The server intercepts incoming POST requests using a `before_request` hook. It compares the request's `Origin` and `Referer` headers against the server's dynamic host URL (`request.host_url`).
* **Protection**: If an external malicious website attempts to trigger compression or directory access requests in the background, the browser automatically attaches the true origin header (e.g. `https://malicious.com`), which the backend detects and rejects with a `403 Forbidden` response.

### Input Path Validation & Traversal Prevention
The CLI and Web Portal APIs restrict source and destination directories to prevent arbitrary directory enumeration, exfiltration, and directory traversal.
* **Mechanism**: Input directories are passed to `is_safe_path()`. This checks that paths do not point to system-critical directories or direct home roots.
* **Restricted Roots**: Paths directly under or equal to `/Users`, `/System`, `/Library`, and the root directory `/` are blocked.
* **Protection**: Malicious or accidental requests targeting folders like `/etc`, a user's home directory, or private configuration directories are caught at the API layer and rejected with a `400 Bad Request` before filesystem scans or subprocesses start.

### Secure Default Service Binding
By default, the Flask application binds only to the local loopback interface.
* **Mechanism**: Default host configuration binds to `127.0.0.1` and disables debug mode.
* **Protection**: Prevents accidental exposure of the web interface to the local network or the internet. The interactive Python debugger console is disabled to mitigate Remote Code Execution (RCE) risks.

---

## 2. Hardened Configuration Guide

If you need to customize the network or debugging settings, use standard environment variables:

| Environment Variable | Description | Default | Hardened Value |
| :--- | :--- | :--- | :--- |
| `FLASK_SECRET_KEY` | Secret key used to sign session cookies. | Cryptographically random key | Custom secure string |
| `FLASK_DEBUG` | Enables Werkzeug interactive debugger. | `False` | `False` |
| `FLASK_HOST` | Network interface IP to bind the server to. | `127.0.0.1` | `127.0.0.1` |

### Running the server with custom overrides:
```bash
# Enable debug mode on localhost for development
FLASK_DEBUG=1 python run_web.py

# Bind to all network interfaces (Caution: exposes debugger if enabled)
FLASK_HOST=0.0.0.0 python run_web.py
```

---

## 3. Safe AI Data Handling Practices

Developers using Sakura Sumi to prepare codebases for LLM consumption should follow these best practices:

1. **Clean Exclusions List**: Always review `.env`, `.git`, credentials, and keys to ensure they are excluded from the scanned source files. Check `src/utils/file_discovery.py` for default exclusions or use the `--exclude` flag.
2. **Review Generated PDFs**: Inspect compiled PDFs in the output directory before uploading them to external AI interfaces to verify that no secrets or customer data have been captured.
3. **Verify Third-Party Repositories**: When compressing open-source repositories from untrusted sources, review code comments and documentation files to verify there are no hidden prompt injection payloads that could manipulate downstream AI agents.
