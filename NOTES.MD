# NOTES.MD - Project Overview

**Last Updated**: 2025-01-15  
**Project**: OCR Compression  
**Status**: Initial Setup

---

## Project Identity

**Name**: OCR Compression  
**Purpose**: Build an OCR-based codebase compression system that converts source code into dense PDFs and optionally applies DeepSeek-OCR compression for LLM analysis. Achieves 7-20x token compression, enabling large codebases to fit within Gemini's 2M token context window.  
**Technology Stack**: Python (reportlab, pyyaml, pillow), Optional: DeepSeek-OCR (vllm, huggingface-cli), Flask/FastAPI (for web portal), CLI tools  
**Current Phase**: ✅ **COMPLETE** - All 10 stories implemented

---

## Current Status

### Recent Activity
- 2025-01-15: Sakura UI Theme Implementation
  - Added beautiful cherry blossom theme to web portal
  - Implemented falling petals animation on form submission
  - Added haiku at top of page (easily removable)
  - Updated all UI components with sakura color palette
  - Created DEVELOPER.md welcome guide for new developers
  - Updated all documentation with sakura theme information
- 2025-01-15: Initial project structure setup
  - Established three-layer documentation hierarchy (CANON.md, NOTES.MD, WORKING.md)
  - Created notes.yaml central registry
  - Set up bugs/ and archive/ directory structures
  - Initialized meta-process framework
- 2025-01-15: Epic planning and story breakdown
  - Created EPIC-001: OCR-Based Codebase Compression System
  - Broke down into 10 stories covering full compression pipeline
  - Target: Love Oracle AI codebase compression (~102 source files)
- 2025-01-15: Implementation of first three stories
  - ✅ STORY-001: Environment Setup & Dependencies
  - ✅ STORY-002: File Discovery & Inventory System
  - ✅ STORY-003: Dense PDF Conversion Engine
  - Successfully tested on Love Oracle AI: 108 files converted (100% success rate)
- 2025-01-15: Implementation of stories 4-6
  - ✅ STORY-004: Batch Processing Pipeline Enhancements (parallel, resume, retry, progress bars)
  - ✅ STORY-005: DeepSeek-OCR Integration (optional, graceful degradation)
  - ✅ STORY-006: Browser Portal / Launcher Interface (Flask web app with modern UI)

### Active Work
- ✅ **EPIC-001 COMPLETE**: All 10 stories implemented and tested
- ✅ Core compression pipeline with advanced features (parallel, resume, retry)
- ✅ Web portal with modern UI
- ✅ Metrics & reporting with token estimation and visualizations
- ✅ Comprehensive test suite (pytest) - 24 tests, 63% coverage
- ✅ Complete documentation (README, Usage Guide, API, Troubleshooting)
- ✅ Love Oracle AI specific configuration preset
- ✅ Production-ready system

### Blockers
- None currently

---

## Setup Instructions

### Prerequisites
- Python 3.8+ 
- pip package manager
- Access to Love Oracle AI codebase directory: `/Users/johndoe/Projects/LoveOracleAI copy`

### Environment Setup
```bash
# Create Python virtual environment
cd /Users/johndoe/Projects/OCR\ Compression
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR: venv\Scripts\activate  # On Windows

# Install required dependencies
pip install reportlab pyyaml pillow

# Optional: Install DeepSeek-OCR dependencies
pip install vllm
huggingface-cli download deepseek-ai/DeepSeek-OCR
```

### Invocation Rites

**Basic Usage:**
```bash
# Activate virtual environment
cd /Users/johndoe/Projects/OCR\ Compression
source venv/bin/activate

# Run compression on Love Oracle AI codebase
python compress.py "/Users/johndoe/Projects/LoveOracleAI copy" -v

# Enable parallel processing
python compress.py "/path/to/source" --parallel --workers 4 -v

# Resume from checkpoint
python compress.py "/path/to/source" --resume -v

# Enable OCR compression (optional, requires dependencies)
python compress.py "/path/to/source" --ocr --ocr-mode small -v

# Specify custom output directory
python compress.py "/Users/johndoe/Projects/LoveOracleAI copy" -o "/path/to/output" -v

# Add additional exclusions
python compress.py "/path/to/source" --exclude "test" "spec" -v

# Run web portal
python run_web.py
# Then open http://localhost:5000 in your browser
```

**CLI Options:**
- `source_dir` (required): Source codebase directory to compress
- `-o, --output`: Output directory for PDFs (default: `{source_dir}_ocr_ready`)
- `-v, --verbose`: Verbose output with progress and statistics
- `--exclude`: Additional exclusion patterns (space-separated)

**Example Output:**
- Discovers all source files (TypeScript, TSX, JSON, YAML, CSS, HTML)
- Filters out build artifacts, node_modules, Android files, etc.
- Generates dense PDFs with 8pt font, minimal margins
- Provides statistics: file counts, sizes, compression ratios

---

## Architecture Highlights

### Compression Pipeline Architecture

1. **File Discovery Layer**: Scans source directory, filters exclusions, creates inventory
2. **PDF Conversion Engine**: Converts source files to dense, OCR-optimized PDFs
3. **Batch Processing**: Parallel/sequential processing with progress tracking
4. **Optional OCR Compression**: DeepSeek-OCR integration for maximum compression (7-20x)
5. **Reporting & Metrics**: Compression ratios, token estimates, Gemini compatibility checks
6. **User Interface**: CLI launcher or web portal for easy execution

### Key Components

- **Dense PDF Generator**: reportlab-based converter with minimal margins, small fonts
- **File Type Handlers**: Specialized processors for JSON, YAML, TypeScript, TSX, CSS, HTML
- **Compression Engine**: Optional DeepSeek-OCR integration for visual token compression
- **Reporting System**: Metrics calculation, token estimation, compatibility validation

---

## Critical Failure Patterns

[To be documented as patterns are identified]

---

## Key Files & Directories

- `CANON.md` - Immutable project rules and specifications
- `PROJECT_DESIGN_RULEBOOK.md` - Single source of truth (SSOT) for all frontend design, styling, and UI implementation
- `DEVELOPER.md` - Developer welcome guide and contribution guidelines
- `WORKING.md` - Active tasks and working notes
- `notes.yaml` - Documentation registry
- `bugs/` - Bug tracking YAML files (currently 0 bugs)
- `archive/` - Historical records

---

**Note**: This file provides high-level overview only. For active tasks, see WORKING.md. For immutable rules, see CANON.md.

