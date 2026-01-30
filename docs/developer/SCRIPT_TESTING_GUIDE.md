# Testing shell scripts

Scripts that “should work” often fail in the wild because deps are missing, paths are wrong, or the caller (e.g. Automator) doesn’t pass arguments the way you expect.

Before committing a script:

1. **Syntax** — `bash -n scripts/your_script.sh`
2. **Happy path** — Run it with a real directory and confirm the expected output (e.g. PDFs in the right place).
3. **Error cases** — Missing dir, missing deps, wrong path. Script should exit with a clear message, not a raw Python traceback.
4. **Context** — If it’s used from Automator or Finder, test that too, or at least test with the same arguments (e.g. one quoted path).

Use absolute paths (resolve with `cd` and `pwd`). Validate arguments (e.g. `-d "$1"` for a directory). Check for required commands and Python modules and print “run this to fix it” instead of failing with a cryptic error.

A script that only handles errors on paper but never runs end-to-end is still broken. Run it once with deps installed and real input before you commit.
