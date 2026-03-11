# Contributing

Fork, clone, then:

```bash
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install pytest pytest-cov
```

Code: PEP 8, type hints where it helps, docstrings on public APIs. Keep functions small.

Tests: add them for new behavior, run with `pytest tests/`. Coverage: `pytest --cov=src tests/`. Everything should pass before you open a PR.

Bugs: we use the `bugs/` dir with `BUG-XXX.yaml` files. Use the template there; include steps, expected vs actual, and your environment.

PRs: branch from `main`, make your change, run tests, update docs if needed, then open a PR with a clear description. Mention bug IDs if it fixes one.

Commits: clear messages. Prefer “Fix BUG-XXX: short description” when applicable.

Questions: open an issue.
