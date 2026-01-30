# Validation gap (script work)

We added a script with solid error handling (dependency checks, path checks, nice messages) but didn’t actually run it end-to-end with deps installed. So it failed in the field for the “everything is set up” case.

Takeaway: test the happy path too. Install deps, run the script, confirm the output (e.g. PDFs) exists. Error handling alone isn’t enough.

Before committing a script: run it in a real environment, with deps present, and verify the expected side effects (files created, exit code, etc.).
