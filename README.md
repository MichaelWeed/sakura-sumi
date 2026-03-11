# Sakura Sumi

![Sakura Sumi](flag.jpg)

🌸 Sakura Sumi - Visual Token Arbitrage Engine transforms raw source code into high-density visual tokens for LLM context maximization. Achieve 7–20x token compression, letting entire repositories fit comfortably inside a 2M-token context window with perfect retrieval.

The engine discovers files, applies deterministic arbitrage algorithms to maximize information density, and generates vision-optimized PDFs. Features include multi-worker parallelization, a beautiful Sakura-themed Web UI, DeepSeek-OCR integration, and a dedicated "Prompt Collector" for text fragments. See [Arbitrage Methodology](#arbitrage-methodology) for technical details.

## File Type Support

Only text-based files with known extensions are processed. Everything else is skipped so we don’t blow up on binaries or random junk.

### Supported File Types

**Source Code:**
- TypeScript/JavaScript: `.ts`, `.tsx`, `.js`, `.jsx`
- Python: `.py`, `.pyx`
- Java/Kotlin: `.java`, `.kt`
- Systems Languages: `.go`, `.rs`, `.cpp`, `.c`, `.h`, `.hpp`
- Other Languages: `.rb`, `.php`, `.swift`, `.dart`

**Configuration Files:**
- `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`
- `.xml`, `.properties`, `.env`, `.config`

**Stylesheets:**
- `.css`, `.scss`, `.sass`, `.less`, `.styl`

**Markup & Documentation:**
- `.html`, `.htm`, `.xhtml`, `.md`, `.markdown`, `.txt`

**Document Formats:**
- `.docx` - Microsoft Word documents (text extraction supported)

### Automatically Excluded

The following are **automatically excluded** and will not be processed:

- **Binary files**: Any file without a supported extension (images, executables, archives, etc.)
  - Examples: `.jpg`, `.png`, `.pdf`, `.exe`, `.dll`, `.so`, `.zip`, `.tar`, `.xlsx`
- **Build artifacts**: `node_modules`, `dist`, `build`, `out`, `bin`, `obj`
- **Version control**: `.git`, `.svn`, `.hg`
- **Cache directories**: `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.next`, `.nuxt`
- **Virtual environments**: `.venv`, `venv`, `env`
- **IDE directories**: `.idea`, `.vscode`, `.vs`
- **Other**: `.gradle`, `gradle`, `coverage`, `.nyc_output`, `*.log`, `*.tmp`, `*.swp`, `*.swo`, `.DS_Store`

You can add additional exclusion patterns using the `--exclude` CLI option.

### Error Handling

The system handles problematic files gracefully without crashing:

- **Encoding issues**: Attempts multiple encodings (UTF-8, latin-1, cp1252, iso-8859-1). If all fail, the file is skipped with a warning.
- **Permission errors**: Files that cannot be read are skipped with a warning.
- **Very large files**: Files >100MB may cause issues (see Troubleshooting section).
- **Empty files**: Files with 0 bytes are automatically skipped.

So: we only convert files that match the list above. If your repo has 72k files, we’ll only touch the ones that look like source, config, or docs. No images, no binaries, no archives.

## Quick Start

You need Python (from [python.org](https://www.python.org/downloads/) if you don’t have it; check “Add Python to PATH” when installing). Then:

```bash
git clone https://github.com/MichaelWeed/sakura-sumi.git
cd sakura-sumi

python3 -m venv venv
source venv/bin/activate   # macOS/Linux; on Windows: venv\Scripts\activate
pip install -r requirements.txt

python scripts/compress.py "/path/to/your/codebase" -v
```

PDFs show up in a folder named `{your_codebase}_ocr_ready/`.

### Double-click launchers (install + web UI)

No terminal needed. Double-click the right file for your OS; it will create a venv and install deps if needed, then open the web portal (and your browser).

| OS      | File                     |
|---------|--------------------------|
| macOS   | `Sakura Sumi.command`    |
| Windows | `Sakura Sumi.bat`        |
| Linux   | `Sakura Sumi.sh`         |

On Linux, make sure the script is executable (`chmod +x "Sakura Sumi.sh"`). To add it to your application menu, run `./install-linux-launcher.sh` once.

**CLI usage:**
```bash
# Simple compression
python scripts/compress.py "/path/to/codebase" -v

# Parallel processing (faster for large codebases)
python scripts/compress.py "/path/to/codebase" --parallel --workers 4 -v

# Resume from checkpoint (if interrupted)
python scripts/compress.py "/path/to/codebase" --resume -v

# Generate metrics report
python scripts/compress.py "/path/to/codebase" --generate-report markdown -v

# Generate visualization charts
python scripts/compress.py "/path/to/codebase" --generate-charts -v
```

Full options are in [CLI Options](#cli-options). For OCR modes see [Compression Modes](#compression-modes).

### Web portal

If you’d rather not use the CLI:

```bash
# Start the web server
python scripts/run_web.py

# Open http://localhost:5001 in your browser
```

You get a browser UI with folder picker, progress, token estimates, and job history. Same features as the CLI, just through the UI.

### Docker

No local Python? Use Docker.

```bash
# Build the image
docker build -t sakura-sumi .

# Run the web portal (maps port 5001 and persists build artifacts)
docker run --rm -p 5001:5001 \
  -v "$(pwd)/build:/app/build" \
  -v "$(pwd)/output:/app/output" \
  sakura-sumi
```

Or `docker compose up --build`. The compose setup mounts `./build` and `./output` so job history and results stick around. Override with `FLASK_SECRET_KEY` or `SAKURA_TELEMETRY` in `.env` if you need to.

In the web portal, the **Prompt Collector** lets you paste long text (prompts, docs, etc.) and compress it to PDF without pointing at a directory. Click the button, add prompts, then “Compress Prompts.”

## Telemetry

Diagnostic info (timing, file counts, errors, metrics) is written locally to `telemetry.log` in the output directory. Nothing is sent off-machine. JSONL, one object per line.

To turn it off:
```bash
# Disable telemetry logging
export SAKURA_TELEMETRY=0
python scripts/compress.py "/path/to/codebase" -v

# Or set to false/off
export SAKURA_TELEMETRY=false
# OR
export SAKURA_TELEMETRY=off
```


## CLI Options

**Required:**
- `source_dir`: Source codebase directory to compress

**Output:**
- `-o, --output`: Output directory for PDFs (default: `{source_dir}_ocr_ready`)
- `-v, --verbose`: Verbose output with progress and statistics

**Processing:**
- `--parallel`: Enable parallel processing (faster for large codebases)
- `--workers N`: Number of parallel workers (default: CPU count - 1)
- `--batch-size N`: Batch size for sequential processing (default: 10)
- `--resume`: Resume from checkpoint if available (useful if interrupted)
- `--retry N`: Number of retries for failed files (default: 3)

**Compression:**
- `--ocr`: Enable DeepSeek-OCR compression (requires additional dependencies)
- `--ocr-mode {small|medium|large|maximum}`: OCR compression mode (default: small)
  - `small`: 7x compression, 97% accuracy (recommended)
  - `medium`: 10x compression, 97% accuracy
  - `large`: 15x compression, 85-90% accuracy
  - `maximum`: 20x compression, 60% accuracy (not recommended for code)

**Reporting:**
- `--generate-report {json|markdown|html}`: Generate metrics report
- `--generate-charts`: Generate visualization charts

**Filtering:**
- `--exclude`: Additional exclusion patterns (space-separated, .gitignore-style)

## Compression Modes

### PDF Compression (Default)
- Converts source files to dense PDFs
- Minimal margins, small fonts for maximum density
- Suitable for most use cases

### OCR Compression (Optional)
Requires additional dependencies: `pip install vllm transformers`

- **Small**: 7x compression, 97% accuracy (recommended for code)
- **Medium**: 10x compression, 97% accuracy
- **Large**: 15x compression, 85-90% accuracy
- **Maximum**: 20x compression, 60% accuracy (not recommended for code)

## Project Structure

```
OCR Compression/
├── src/                  # Source code (Python package)
│   ├── compression/      # Core compression modules
│   ├── utils/            # Utility modules (discovery, metrics)
│   ├── web/              # Web portal (Flask app)
│   └── main.py           # CLI entry point
├── tests/                # Test suite (mirrors src structure)
├── scripts/              # Executable scripts
│   ├── compress.py       # CLI convenience script
│   └── run_web.py        # Web portal launcher
├── config/               # Configuration files
│   ├── deepseek_ocr.json
│   └── love_oracle_ai.yaml
├── docs/                 # Documentation (organized by audience)
│   ├── user/             # User documentation
│   ├── developer/         # Developer documentation
│   ├── api/              # API documentation
│   └── design/           # Design documentation
├── bugs/                 # Bug tracking (BUG-XXX.yaml format)
├── archive/              # Historical records and completed items
├── build/                # Build artifacts (gitignored)
├── dist/                 # Distribution packages (gitignored)
├── setup.py              # Package setup configuration
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Testing

**For Contributors:** We maintain comprehensive test coverage (currently 81%). All tests must pass before merging PRs.

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_file_discovery.py

# Run with coverage report
pytest --cov=src tests/

# Run with detailed output
pytest tests/ -v
```

**Test Structure:**
- Unit tests for individual components
- Integration tests for pipeline workflows
- End-to-end tests for CLI and web portal
- All tests use pytest fixtures for clean setup/teardown

## Integration with Gemini (Google's AI Model)

**Why compress?** Gemini has a 2M token context window. Large codebases can exceed this limit. Sakura Sumi compresses your code to fit within this window.

**Step-by-step:**

1. **Compress your codebase:**
   ```bash
   python scripts/compress.py "/path/to/codebase" -v
   ```

2. **Check if it fits:**
   ```bash
   python scripts/compress.py "/path/to/codebase" --generate-report markdown -v
   ```
   Look for "Gemini Compatibility" section - it will show ✅ if PDFs fit within 2M tokens.

3. **Upload to Gemini:**
   - Go to [gemini.google.com](https://gemini.google.com)
   - Click the upload button
   - Select PDFs from your output directory (usually `{codebase}_ocr_ready/`)
   - Gemini processes PDFs as images at ~258 tokens per image

**Pro Tip:** Use the web portal's token estimation feature to check compatibility before compressing!

## Examples

### Beginner Examples

**Simple compression:**
```bash
python scripts/compress.py "/Users/johndoe/my-project" -v
```

**Compress and see detailed report:**
```bash
python scripts/compress.py "/Users/johndoe/my-project" \
    --generate-report markdown \
    -v
```

### Advanced Examples

**Large codebase with parallel processing:**
```bash
python scripts/compress.py "/path/to/large-codebase" \
    --parallel --workers 8 \
    --generate-report markdown \
    --generate-charts \
    -v
```

**Resume interrupted compression:**
```bash
# First run (gets interrupted)
python scripts/compress.py "/path/to/codebase" -v

# Resume from where it left off
python scripts/compress.py "/path/to/codebase" --resume -v
```

**Maximum compression with OCR:**
```bash
python scripts/compress.py "/path/to/codebase" \
    --ocr --ocr-mode medium \
    --parallel --workers 4 \
    -v
```

**Exclude specific patterns:**
```bash
python scripts/compress.py "/path/to/codebase" \
    --exclude "*.test.js" "docs/" "*.spec.ts" \
    -v
```

## Troubleshooting

**“No files found”** — The directory has no supported extensions. Use something that has `.py`, `.js`, `.ts`, etc. (see [File Type Support](#file-type-support)).

**No PDFs / weird failures** — Look at `failed_files.json` in the output folder and at `telemetry.log` for details. Permissions and encoding can trip things up; `ls -la` on the source dir is a quick check.

**Parallel runs failing** — Try `--workers 2` or drop `--parallel`.

**OCR not available** — Optional. Install with `pip install vllm transformers` if you want it. Plain PDF compression doesn’t need it.

**Out of memory** — Lower `--batch-size` and `--workers`, or run on a smaller subset of the tree.

**Permission denied** — Fix read access on the source files; `failed_files.json` will list what failed.

More: `docs/user/TROUBLESHOOTING.md`. Right-click / Quick Action issues: `docs/user/RIGHT_CLICK_COMPRESS.md`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## CI/CD Status

![Tests](https://github.com/MichaelWeed/sakura-sumi/workflows/Tests/badge.svg)
![Linting](https://github.com/MichaelWeed/sakura-sumi/workflows/Linting/badge.svg)

---

## Contributing

See `CONTRIBUTING.md` for setup, style, and how to send a PR. Run the test suite before submitting. More for people hacking on the code: `docs/developer/DEVELOPER.md`.

Bugs and questions: look in `docs/` and `bugs/`, or open an issue on GitHub.

