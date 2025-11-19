# Project Structure Guide

This document explains the enterprise-standard organization of the OCR Compression project.

**Last Updated**: 2025-11-16

## Directory Organization

### Root Level
- **README.md** - Main project documentation
- **setup.py** - Python package configuration
- **requirements.txt** - Python dependencies
- **.gitignore** - Git ignore rules
- **STRUCTURE.md** - This file

### Source Code (`src/`)
Python package containing all application code:
- `compression/` - Core compression modules
- `utils/` - Utility modules (discovery, metrics, token estimation)
- `web/` - Flask web application
- `main.py` - CLI entry point

### Scripts (`scripts/`)
Executable scripts for running the application:
- `compress.py` - CLI convenience script
- `run_web.py` - Web portal launcher

### Configuration (`config/`)
Configuration files and presets:
- `deepseek_ocr.json` - DeepSeek-OCR configuration
- `love_oracle_ai.yaml` - Example preset configuration

### Documentation (`docs/`)
Documentation organized by audience:
- `user/` - User-facing documentation (usage guides, troubleshooting)
- `developer/` - Developer documentation (setup, contribution guidelines)
- `api/` - API reference documentation
- `design/` - Design system and UI documentation

### Project Management (`bugs/`, `archive/`)
Project management files:
- `bugs/` - Bug tracking YAML files (BUG-XXX.yaml format)
- `archive/` - Historical records and completed items
- `notes.yaml` - Canonical project notes (gitignored)

### Tests (`tests/`)
Test suite mirroring source structure:
- Unit tests for each module
- Integration tests for pipeline
- Test fixtures and utilities

### Build Artifacts (`build/`, `dist/`)
Generated files (gitignored):
- `build/` - Build artifacts, coverage reports, test output
- `dist/` - Distribution packages (wheels, eggs)

## Best Practices Followed

1. **Separation of Concerns**: Source, tests, docs, configs clearly separated
2. **Package Structure**: Standard Python package layout with `src/`
3. **Documentation Hierarchy**: Organized by audience and purpose
4. **Build Isolation**: Build artifacts in dedicated directories
5. **Project Management**: Meta files separated from deployable code
6. **Configuration Management**: Configs in dedicated `config/` directory
7. **Script Organization**: Executable scripts in `scripts/` directory

## File Naming Conventions

- **Python modules**: `snake_case.py`
- **Directories**: `lowercase/` or `snake_case/`
- **Documentation**: `UPPERCASE.md` for important docs, `Title_Case.md` for others
- **Config files**: `lowercase.extension` (json, yaml, etc.)

## Import Paths

All imports use absolute paths from project root:
```python
from src.compression.pipeline import CompressionPipeline
from src.utils.file_discovery import FileDiscovery
```

## Running the Application

```bash
# CLI
python scripts/compress.py "/path/to/codebase" -v

# Web Portal
python scripts/run_web.py
```

## Building the Package

```bash
# Install in development mode
pip install -e .

# Build distribution
python setup.py sdist bdist_wheel
```

