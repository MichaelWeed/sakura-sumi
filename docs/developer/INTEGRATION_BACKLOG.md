# Integration Readiness Backlog

**Audience**: External platform teams (xAI, Meta) evaluating OCR Compression integration.
**Last Updated**: 2025-11-16

---

## Item IB-01 — Harden Source Directory Access (Priority: Critical)
- **Objective**: Restrict `/api/estimate` and `/api/compress` to authorized storage roots to protect host data.
- **Current State**: Endpoints accept any filesystem path and resolve it server-side.
- **Getting Started**:
  - Add allowlist configuration (env or tenant metadata) defining permitted roots.
  - Enforce path normalization and guard against symlink escapes.
  - Provide 403 responses with guidance for partners when paths fall outside the sandbox.
- **Integration Notes**: xAI/Meta can prototype by configuring tenant-scoped volumes (e.g., S3 mounts, NFS shares) once the guardrail hook is exposed.

## Item IB-02 — Hosted-Friendly Directory & Download UX (Priority: High)
- **Objective**: Replace GUI-dependent helpers with browser-facing flows that work on headless infrastructure.
- **Current State**: `/api/browse-directory` and `/api/open-folder` trigger server-side dialogs/commands.
- **Getting Started**:
  - Introduce signed upload/download endpoints or pre-signed storage URLs.
  - Provide REST/CLI instructions for partners to seed jobs without GUI fallbacks.
  - Gate legacy helpers behind a local-only feature flag for on-prem demos.
- **Integration Notes**: Meta hackathon teams can wire their own storage adapters when REST hooks are documented.

## Item IB-03 — Durable Job Orchestration & Metrics (Priority: High)
- **Objective**: Persist job state in shared infrastructure for resilience and scale-out.
- **Current State**: In-memory dictionary with opportunistic JSON dump to `build/jobs.json`.
- **Getting Started**:
  - Swap to Redis or SQL-backed job table with optimistic locking.
  - Emit structured job lifecycle events (queued/running/completed/failed) for observability.
  - Document retry semantics and cancellation hooks for partner automation.
- **Integration Notes**: xAI can connect their orchestration layer by polling or subscribing to the shared store once endpoints expose job IDs consistently.

## Item IB-04 — Centralize Secret & Session Configuration (Priority: Medium)
- **Objective**: Externalize Flask `secret_key` and related credentials for multi-instance deployments.
- **Current State**: Secret key regenerated on each boot via `os.urandom(24)`.
- **Getting Started**:
  - Load secrets from environment or secret manager (e.g., AWS Secrets Manager, HashiCorp Vault).
  - Provide template `.env.example` outlining required values for session stability.
  - Add health check that warns when runtime falls back to ephemeral secrets.
- **Integration Notes**: Partners can inject their SSO/session requirements once configuration hooks exist.

## Item IB-05 — Integration Quickstart Playbooks (Priority: Medium)
- **Objective**: Publish concise guides covering deployment, storage wiring, auth handoff, and health monitoring.
- **Current State**: Core docs focus on internal pipeline; little guidance for external teams.
- **Getting Started**:
  - Create `docs/integration/` with quickstart, API overview, and Terraform/Docker skeletons.
  - Include sample environment vars, curl collection, and troubleshooting table.
  - Reference bug IDs and feature flags so partners track hardening roadmap.
- **Integration Notes**: Provides week-one lift for Meta hackathon participants and xAI pilots.

---

**Next Review**: Align backlog priorities once security hardening (IB-01) lands; reassess remaining items based on partner feedback and pilot requirements.
