# Open Source Distribution Checklist

This document tracks the cleanup and preparation for open source distribution.

## ✅ Completed Tasks

### System-Specific Paths Removed
- [x] Updated HTML template example paths (`/Users/john/myproject` → `/path/to/myproject`)
- [x] Updated documentation example paths (`/Users/johndoe/Projects/LoveOracleAI copy` → `/path/to/test/codebase`)
- [x] Updated bug files to remove specific test paths
- [x] Updated config file to be a generic template

### Environment Information Generalized
- [x] Updated all bug files to use generic OS info (`macOS / Linux / Windows` instead of specific versions)
- [x] Updated Python version references (`Python 3.8+` instead of `Python 3.14`)
- [x] Updated browser references to be generic (`All browsers` or `Chrome / Firefox / Safari`)

### Documentation Cleanup
- [x] Updated README.md with generic installation instructions
- [x] Created CONTRIBUTING.md for contribution guidelines
- [x] Updated notes.yaml to remove personal/system-specific information
- [x] Cleaned up config/love_oracle_ai.yaml to be a generic template

### Git Configuration
- [x] Verified .gitignore excludes:
  - `build/jobs.json` (contains user-specific paths)
  - `notes.yaml` (contains project notes)
  - `build/` and `dist/` directories
  - `venv/` and other build artifacts

### Code Review
- [x] No hardcoded system-specific paths in source code
- [x] All path handling uses `Path().expanduser().resolve()` for portability
- [x] OS detection uses `platform.system()` for cross-platform compatibility

## 📝 Items to Update Before Publishing

1. **Repository URL**: Update placeholder URLs in:
   - `README.md` (line 27): Replace `https://github.com/yourusername/ocr-compression.git`
   - `setup.py` (line 27): Replace `https://github.com/yourusername/ocr-compression`

2. **Author Information**: Update in `setup.py`:
   - `author` field (currently "Sakura Sumi Contributors")
   - `author_email` field (currently empty)

3. **License File**: Ensure `LICENSE` file exists (MIT License mentioned in README)

4. **Repository Description**: Update GitHub repository description and topics

## 🔒 Security Notes

The following items are documented as known limitations (see bugs/):
- BUG-001: Path access via /api/compress allows arbitrary filesystem reads (wont-fix - enterprise item)
- BUG-003: Job storage not safe for multi-instance deployments (wont-fix - enterprise item)

These are acceptable for single-user/local deployments but should be addressed for hosted/multi-tenant deployments.

## ✅ Ready for Distribution

The project is now ready for open source distribution. All system-specific paths and personal information have been removed or generalized.

