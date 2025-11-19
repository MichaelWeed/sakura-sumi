# Usage Guide

Complete guide for using the OCR Compression System.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Web Portal](#web-portal)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 500MB+ free disk space

### Step-by-Step Installation

```bash
# 1. Navigate to project directory
cd /path/to/OCR\ Compression

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python compress.py --help
```

## Basic Usage

### Simple Compression

```bash
python compress.py "/path/to/codebase" -v
```

This will:
- Discover all source files
- Convert them to PDFs
- Save to `{codebase}_ocr_ready` directory
- Display progress and statistics

### With Custom Output

```bash
python compress.py "/path/to/codebase" -o "/path/to/output" -v
```

### Excluding Files

```bash
python compress.py "/path/to/codebase" --exclude "test" "spec" "*.log" -v
```

## Advanced Features

### Parallel Processing

Speed up compression for large codebases:

```bash
python compress.py "/path/to/codebase" --parallel --workers 4 -v
```

- `--parallel`: Enable parallel processing
- `--workers N`: Number of worker threads (default: CPU count - 1)

### Resume Capability

Resume interrupted compressions:

```bash
# First run (interrupted)
python compress.py "/path/to/codebase" -v
# ... Ctrl+C ...

# Resume from checkpoint
python compress.py "/path/to/codebase" --resume -v
```

### Retry Logic

Handle transient failures:

```bash
python compress.py "/path/to/codebase" --retry 5 -v
```

### Metrics & Reporting

Generate comprehensive reports:

```bash
# Markdown report
python compress.py "/path/to/codebase" --generate-report markdown -v

# JSON report
python compress.py "/path/to/codebase" --generate-report json -v

# HTML report
python compress.py "/path/to/codebase" --generate-report html -v

# With charts
python compress.py "/path/to/codebase" --generate-charts -v
```

### OCR Compression (Optional)

For maximum compression (requires additional dependencies):

```bash
# Install OCR dependencies first
pip install vllm transformers

# Enable OCR compression
python compress.py "/path/to/codebase" --ocr --ocr-mode small -v
```

Modes:
- `small`: 7x compression, 97% accuracy (recommended)
- `medium`: 10x compression, 97% accuracy
- `large`: 15x compression, 85-90% accuracy
- `maximum`: 20x compression, 60% accuracy

## Web Portal

### Starting the Portal

```bash
python run_web.py
```

Then open http://localhost:5000 in your browser.

### Portal Features

The web portal features a beautiful **sakura (cherry blossom) theme**:
- **Cherry Blossom Aesthetics**: Soft pink color palette with gentle gradients
- **Falling Petals Animation**: Petals fall when you start compression
- **Modern UI**: Rounded edges, smooth transitions, responsive design
- **Intuitive Interface**: Easy-to-use forms and real-time progress tracking

### Using the Portal

1. **Enter source directory path** - Use the input field or browse button
2. **Estimate tokens** (optional) - Click "Estimate Tokens" to see compression preview
3. **Configure options** - Enable parallel processing, OCR compression, etc.
4. **Click "Start Compression"** - Watch the falling petals animation
5. **Monitor progress** - Real-time progress bars and status updates
6. **Download results** - Get ZIP archive when complete

## Configuration

### Configuration File

Create `.ocr-compress.yaml` in your project root:

```yaml
source_directory: "/path/to/codebase"
exclusions:
  - "node_modules"
  - "dist"
processing:
  parallel: true
  workers: 4
output:
  generate_report: "markdown"
  generate_charts: true
```

### Love Oracle AI Preset

Use the included preset:

```bash
# Copy preset config
cp configs/love_oracle_ai.yaml .ocr-compress.yaml

# Edit as needed
# Then use with compression
```

## Troubleshooting

### PDFs Not Generating

**Symptoms**: No PDF files in output directory

**Solutions**:
- Check file permissions
- Verify source files are readable
- Check error messages in verbose output
- Ensure sufficient disk space

### Memory Issues

**Symptoms**: Out of memory errors, system slowdown

**Solutions**:
- Reduce parallel workers: `--workers 2`
- Disable parallel processing
- Process smaller codebases
- Increase system RAM

### Slow Performance

**Symptoms**: Compression takes too long

**Solutions**:
- Enable parallel processing: `--parallel`
- Increase workers: `--workers 8`
- Exclude unnecessary files: `--exclude "test" "spec"`
- Use resume for large codebases: `--resume`

### OCR Not Available

**Symptoms**: OCR compression fails or unavailable

**Solutions**:
- Install dependencies: `pip install vllm transformers`
- Check system requirements (GPU may be needed)
- Use PDF compression instead (sufficient for most cases)

## Best Practices

1. **Test First**: Run on small codebase first
2. **Use Parallel**: Enable for codebases >100 files
3. **Check Metrics**: Verify Gemini compatibility before upload
4. **Resume Large Jobs**: Use resume for very large codebases
5. **Exclude Build Artifacts**: Always exclude dist, build, node_modules

## Examples

### Small Project

```bash
python compress.py "./my-project" -v
```

### Large Project

```bash
python compress.py "./large-project" \
    --parallel --workers 8 \
    --resume \
    --generate-report markdown \
    --generate-charts \
    -v
```

### Production Workflow

```bash
# 1. Compress with metrics
python compress.py "./codebase" \
    --parallel \
    --generate-report markdown \
    -v

# 2. Check metrics report
cat codebase_ocr_ready/metrics_report.md

# 3. Verify Gemini compatibility
# 4. Upload PDFs to Gemini
```

## Integration with Gemini

1. **Compress**: Run compression with metrics
2. **Verify**: Check metrics report for compatibility
3. **Upload**: Upload PDFs to gemini.google.com
4. **Analyze**: Use Gemini with full codebase context

## FAQ

**Q: How accurate is token estimation?**
A: Token estimation uses tiktoken (GPT-4 encoding) for text and visual token estimates for PDFs. Accuracy is approximate but sufficient for planning.

**Q: Can I compress multiple codebases?**
A: Yes, run compression separately for each codebase or combine them into one directory.

**Q: What file types are supported?**
A: Sakura Sumi uses a whitelist approach and only processes text-based files with supported extensions:
- **Source code**: `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.java`, `.kt`, `.go`, `.rs`, `.cpp`, `.c`, `.h`, `.rb`, `.php`, `.swift`, `.dart`
- **Config files**: `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.xml`, `.properties`, `.env`, `.config`
- **Stylesheets**: `.css`, `.scss`, `.sass`, `.less`, `.styl`
- **Markup/Docs**: `.html`, `.htm`, `.xhtml`, `.md`, `.markdown`, `.txt`

Binary files (images, executables, archives, Office files) are automatically excluded. See the README for complete details.

**Q: How do I know if my codebase fits in Gemini?**
A: Check the metrics report - it shows token counts and Gemini compatibility.

**Q: Is OCR compression necessary?**
A: No, PDF compression is sufficient for most use cases. OCR provides additional savings but requires heavy dependencies.

