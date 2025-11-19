# Bug Tracker Summary

## Security Note

**For Open Source Users:** This bug tracker includes security-related issues for transparency. 

- **BUG-001** documents a known limitation for **multi-tenant/hosted deployments** where the service accepts arbitrary filesystem paths. This is **not a security concern for single-user/local deployments** where you control the input paths.
- The issue is marked "wont-fix" because it's deferred as an enterprise integration feature (tenant-scoped storage architecture). See `docs/developer/INTEGRATION_BACKLOG.md` for details.
- **Single-user deployments are safe** - you control what directories you point the tool at.

We believe in transparency and documenting known limitations helps users make informed decisions about deployment scenarios.

---

## Totals
- Total bugs: 11

## By Status
- open: 1
- in-progress: 0
- resolved: 8
- closed: 0
- wont-fix: 2
- duplicate: 0

## By Priority
- critical: 2 (1 resolved, 1 wont-fix - enterprise item)
- high: 3 (2 resolved, 1 wont-fix - enterprise item)
- medium: 4 (3 resolved, 1 open)
- low: 2 (2 resolved)

## Recent Activity
- 2025-02-14: Logged BUG-011 (UI crash when job summary missing). Frontend showResults now has open issue to handle failed jobs gracefully.
- 2025-01-17: Resolved BUG-008 (Missing favicon.ico). Added inline SVG favicon with sakura emoji.
- 2025-01-17: Resolved BUG-009 (Prompt Collector dialog viewport). Fixed flexbox layout to keep footer visible and make body scrollable.
- 2025-01-17: Resolved BUG-010 (Job History buttons). Added accessibility attributes and focus styles.
- 2025-01-17: Logged BUG-008, BUG-009, and BUG-010 during comprehensive end-to-end testing.
- 2025-01-16: Resolved BUG-006 (KeyError in _print_summary for smart concatenation). Fixed missing 'files_already_processed' key.
- 2025-01-16: Resolved BUG-007 (Web UI max_total_pages default mismatch). Fixed UI defaulting to 10 instead of 1000.
- 2025-01-16: Resolved BUG-005 (PDF generation XML escaping bug). Fixed critical issue causing 99/109 files to fail. Success rate improved from 9.2% to 100%.
- 2025-11-16: Logged BUG-001 through BUG-004 during integration readiness review.
- 2025-11-16: Resolved BUG-002 (GUI endpoints) and BUG-004 (secret key).
- 2025-11-16: Deferred BUG-001 and BUG-003 as enterprise integration items (see INTEGRATION_BACKLOG.md).

