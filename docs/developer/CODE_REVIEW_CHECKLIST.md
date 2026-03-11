# Code review (self or AI output)

Quick sanity check before committing.

**Scripts** — Syntax (`bash -n`). Run with valid input and confirm expected side effects. Run with bad input (missing dir, missing deps) and confirm clear errors and exit codes. If it’s used from Automator/Finder, either test that or test with the same kind of arguments.

**Python** — Imports and missing deps: does it fail with a useful message? Paths and inputs validated? Edge cases (empty, None) considered?

**In general** — Does it actually fix the thing it claims to fix? Did you run it? Error messages that help the user fix the problem beat raw stack traces.

Red flags: no validation, no error handling, “this will always exist,” or “it should work” with no test run.

When reviewing AI-generated code: run it, try bad inputs, and check that it does what you asked. Don’t assume it’s right without testing.
