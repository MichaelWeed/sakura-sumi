# 🌸 Sakura Sumi - OCR Compression System


![🌸Sakura Sumi](flag.jpg)

Convert your codebase to compressed PDFs for LLM analysis. Achieves 7-20x token compression, enabling large codebases to fit within Gemini's 2M token context window.

## Features

- **File Discovery**: Automatically discovers and categorizes source files
- **Dense PDF Conversion**: Converts code to OCR-optimized PDFs with minimal margins
- **Parallel Processing**: Process multiple files simultaneously
- **Resume Capability**: Resume interrupted compressions from checkpoints
- **Progress Tracking**: Real-time progress bars and status updates
- **OCR Compression**: Optional DeepSeek-OCR integration for maximum compression (7-20x)
- **Metrics & Reporting**: Token estimation, compression ratios, Gemini compatibility checks
- **Web Portal**: Beautiful sakura-themed browser interface with cherry blossom aesthetics
- **Prompt Collector**: Paste and compress long-form prompts without pointing to a directory
- **Comprehensive Testing**: Unit and integration tests for reliability

## File Type Support

Sakura Sumi uses a **whitelist approach** - only text-based files with supported extensions are processed. This ensures reliable conversion and prevents crashes from binary files.

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

### Important Note

**Sakura Sumi does NOT convert everything that's not in the exclusion list.** It only processes text files with supported extensions. This whitelist approach ensures:
- Reliable conversion (no crashes from binary files)
- Predictable behavior (only text-based source files)
- Optimal compression (text files compress best)

If you have a codebase with 72k files, only those with supported extensions (typically source code, config, and documentation files) will be converted. Binary files, images, and archives are automatically excluded.

## Quick Start

### For Beginners

**What is this?** Sakura Sumi converts your code files into compressed PDFs that you can upload to AI models like Google Gemini. This lets you analyze entire codebases that would normally be too large.

**3-Step Setup:**

1. **Install Python** (if you don't have it):
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Get the code:**
   ```bash
   git clone https://github.com/yourusername/ocr-compression.git
   cd ocr-compression
   ```

3. **Set up and run:**
   ```bash
   # Create a virtual environment (keeps dependencies organized)
   python3 -m venv venv
   
   # Activate it
   source venv/bin/activate  # On macOS/Linux
   # OR: venv\Scripts\activate  # On Windows
   
   # Install required packages
   pip install -r requirements.txt
   
   # Compress your codebase (replace with your actual path)
   python scripts/compress.py "/path/to/your/codebase" -v
   ```

**That's it!** Your PDFs will be in `{your_codebase}_ocr_ready/`

### For Experienced Developers

**Installation:**
```bash
git clone https://github.com/yourusername/ocr-compression.git
cd ocr-compression
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Basic Usage:**
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

**Advanced Options:**
- See [CLI Options](#cli-options) for full parameter list
- See [Compression Modes](#compression-modes) for OCR compression details
- See [Project Structure](#project-structure) for codebase organization

### Web Portal (Recommended for Beginners)

The web portal provides a user-friendly interface - perfect if you're not comfortable with command-line tools.

```bash
# Start the web server
python scripts/run_web.py

# Open http://localhost:5001 in your browser
```

**Features:**
- Beautiful sakura (cherry blossom) themed interface
- Point-and-click file selection
- Real-time progress tracking
- Token estimation before compression
- Job history and results management
- No command-line knowledge required

**For Advanced Users:** The web portal exposes all CLI features through a GUI, including parallel processing, resume capability, and OCR compression modes.

### Prompt Collector (Web Portal Feature)

**What it does:** Compress long-form text prompts without needing a directory structure.

**How to use:**
1. Click the **"Prompt Collector"** button in the web portal
2. Click the **"+"** icon to add a new prompt
3. Paste your text - it saves automatically
4. Click **"Compress Prompts"** to generate PDFs

**Use cases:**
- Compressing long AI prompts for analysis
- Converting documentation snippets to PDFs
- Processing text that isn't in file format

**For Developers:** The drawer uses `window.PromptCollectorStore` for state management, enabling future JSON export or LLM integration hooks.

## Telemetry & Logging

**What is telemetry?** Sakura Sumi logs diagnostic information to help you debug issues and understand compression performance. This is **local-only** - no data is sent anywhere.

**What gets logged:**
- Pipeline start/end times
- Success/failure status
- File counts and processing duration
- Error messages and warnings
- Compression metrics

**Where it's stored:**
- Logs are written to `telemetry.log` in your output directory
- Example: If output is `/path/to/output`, logs are at `/path/to/output/telemetry.log`
- Logs are in JSONL format (one JSON object per line) for easy parsing

**How to disable:**
```bash
# Disable telemetry logging
export SAKURA_TELEMETRY=0
python scripts/compress.py "/path/to/codebase" -v

# Or set to false/off
export SAKURA_TELEMETRY=false
# OR
export SAKURA_TELEMETRY=off
```

**For Developers:** Telemetry is enabled by default to help with debugging. The logger respects the `SAKURA_TELEMETRY` environment variable and never blocks the pipeline if logging fails.

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

### Common Issues

**Problem: "No files found to process"**
- **Cause**: Directory contains no supported file types
- **Solution**: Check that your directory has source code files (`.py`, `.js`, `.ts`, etc.). See [File Type Support](#file-type-support) for full list.

**Problem: PDFs not generating**
- **Cause**: File permissions or encoding issues
- **Solution**: 
  - Check file permissions: `ls -la /path/to/files`
  - Check the `failed_files.json` in output directory for specific errors
  - Review telemetry log for detailed error messages

**Problem: Parallel processing errors**
- **Cause**: Too many workers or system resource limits
- **Solution**: 
  - Reduce workers: `--workers 2`
  - Or disable parallel mode: remove `--parallel` flag

**Problem: OCR compression not available**
- **Cause**: Missing optional dependencies
- **Solution**: Install OCR dependencies: `pip install vllm transformers`
- **Note**: OCR compression is optional - regular PDF compression works without it

**Problem: Out of memory errors**
- **Cause**: Processing too many files at once
- **Solution**: 
  - Reduce batch size: `--batch-size 5`
  - Reduce workers: `--workers 2`
  - Process in smaller chunks

**Problem: "Permission denied" errors**
- **Cause**: Cannot read source files
- **Solution**: 
  - Check file permissions: `chmod +r /path/to/files`
  - Run with appropriate user permissions
  - Check `failed_files.json` for specific files that failed

**Still stuck?**
- Check the telemetry log in your output directory
- Review `failed_files.json` for specific file errors
- Open an issue on GitHub with error details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please see `CONTRIBUTING.md` for:
- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process

For detailed developer documentation, see `docs/developer/DEVELOPER.md`.

Ensure tests pass before submitting PRs.

## Support

For issues and questions:
- Check the documentation in `docs/`
- Review existing bugs in `bugs/`
- Open an issue on GitHub

