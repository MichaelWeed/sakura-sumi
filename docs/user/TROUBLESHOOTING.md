# Troubleshooting

**Venv won’t activate** — Use the full path to the venv, or recreate it: `rm -rf venv && python3 -m venv venv`. Python 3.8+ required.

**pip install fails** — Try `pip install --upgrade pip` and `python3 -m pip install -r requirements.txt`. If it’s one package, e.g. `pip install reportlab`.

**“No files found”** — Path correct? Directory has source files (supported extensions)? Check that exclusions aren’t hiding everything.

**Some PDFs don’t generate** — Encoding (UTF-8 usually), disk space, or binary/weird files. Verbose output and `failed_files.json` in the output dir will point at the files. You can bump `--retry`.

**Out of memory / system slow** — Lower `--workers`, drop `--parallel`, or run on a smaller tree.

**Right-click / Quick Action does nothing** — See [RIGHT_CLICK_COMPRESS.md](RIGHT_CLICK_COMPRESS.md). Often it’s Automator not passing the folder; the double-click script avoids that.

**Permission denied** — Fix read access on the source files. `failed_files.json` lists what failed.

Logs: `telemetry.log` in the output directory, and for the Quick Action script, `~/Library/Logs/sakura-sumi-quick-action.log`.
