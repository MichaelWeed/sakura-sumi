# compress_with_defaults.sh — validation

Script was validated on 2026-01-22. Venv was recreated, deps installed from `requirements.txt`, then run against a small test dir. PDFs showed up in the expected `{source}_ocr_ready` folder and were valid.

Along the way we fixed: venv pointing at system Python, missing deps, and main.py still importing removed modules (density_profiles, security). Those are fixed; the script runs successfully for both error cases (missing dir, missing deps) and the success path.
