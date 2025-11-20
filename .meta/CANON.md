# CANON.md - Immutable Codex of Finalized Edicts

**Purpose**: This document contains immutable, verified, finalized edicts that govern the project. Never delete content, only append with versioned decrees.

**Last Updated**: 2025-01-15

---

## Version History

### Version 1.0 - 2025-01-15
- **Decree**: Initial canonization of project structure and meta-process framework
- **Rationale**: Establishing immutable foundation for project tracking and documentation
- **Source**: Meta-Process Prompt: Project Tracking & Update Protocol
- **Impact**: Defines three-layer documentation hierarchy, bug tracking system, canonization ritual, QA framework

---

## Core Principles

### Three-Layer Documentation Hierarchy

1. **CANON.md** - Immutable, verified, finalized edicts (never delete, only append with versioned decrees)
2. **NOTES.MD** - High-level overview, quarterly updates, invocation rites, current status
3. **WORKING.md** - Transient working notes for active tasks, hypotheses, session outcomes (prune regularly)

**Rule**: Information flows UPWARD only: WORKING.md → CANON.md (via canonization ritual), WORKING.md → NOTES.MD (for high-level updates), never downward.

### Metadocument Exclusion

**Decree**: None of the metadocuments or processes (CANON.md, NOTES.MD, WORKING.md, notes.yaml, bugs/, archive/, Session_*_Prompt.md, TEST_*.md) shall be included in any deployable package.

**Rationale**: These are project management artifacts, not application code or runtime dependencies.

---

## Project Structure Requirements

### Required Directories

- `bugs/` - Bug tracking YAML files (BUG-XXX.yaml format)
- `archive/` - Historical records with subdirectories:
  - `archive/notes/` - Completed notes and summaries
  - `archive/session_prompts/` - Historical session prompts
  - `archive/epics/completed/` - Completed epics
  - `archive/epics/superseded/` - Superseded epics
  - `archive/bugs/resolved/` - Resolved bugs

### Required Files

- `notes.yaml` - Central registry of all documentation files
- `CANON.md` - This file (immutable codex)
- `NOTES.MD` - High-level project overview
- `WORKING.md` - Transient working notes
- `bugs/README.md` - Bug tracking statistics and summary

---

## Bug Tracking Schema

All bugs MUST follow the YAML schema defined in the Meta-Process Prompt (Section 2.1). Bug IDs auto-increment from BUG-001.

---

## Canonization Ritual

Content may only be canonized after:
1. Convergence detected (decision finalized, tests passed, no open queries)
2. 100% evidentiary support (all claims verified, no speculation)
3. Conflict check (cross-referenced against CANON.md)
4. Stress test (simulated edge cases)
5. Format compliance (matches CANON.md structure)

See Meta-Process Prompt Section 3 for complete ritual steps.

---

## QA Self-Audit Framework

Every deliverable MUST pass the Seven-Step QA Implementation Loop (Meta-Process Prompt Section 4.2) before handoff.

---

## Command Execution Standards

**CRITICAL**: All commands MUST include:
- Full path with `cd PROJECT_ROOT`
- Environment activation OR full venv/bin paths
- URLs when launching web services (if applicable)
- Stop/kill commands for running processes

Never assume terminal is active or environment is set up.

---

## Test Coverage Management

**Single Source of Truth**: `TEST_COVERAGE_REPORT.md` (or equivalent)

- Contains: Overall coverage %, test counts, per-module coverage, pass rates
- Update: After major test additions or coverage improvements
- Never: Duplicate coverage metrics in other files

---

## Development Standards

### Documentation Updates

Upon completion of epics, stories, or tasks:
1. Meticulously update all associated documentation
2. Proactively generate new tickets for unresolved issues
3. Archive obsolete artifacts

### Code Quality

If deliverables involve code:
1. Rigorously verify test coverage metrics
2. Validate modifications exclusively through CLI
3. Leverage first-principles validation

---

**End of CANON.md**

