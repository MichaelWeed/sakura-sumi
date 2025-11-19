# Developer Guide - 🌸 Sakura Sumi - OCR Compression System

Welcome to 🌸 Sakura Sumi! This guide will help you get started as a developer.

## 🎨 Project Overview

🌸 Sakura Sumi (a nod to the fading ink haiku) converts codebases into compressed PDFs optimized for LLM analysis. The system features a beautiful **sakura-themed web portal** with cherry blossom aesthetics, falling petal animations, and a modern, intuitive interface.

## 🚀 Quick Start for Developers

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for version control)
- A code editor (VS Code, PyCharm, etc.)

### Initial Setup

```bash
# 1. Clone or navigate to the project
cd /path/to/OCR\ Compression

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run tests to verify setup
pytest tests/ -v

# 5. Start the web portal
python scripts/run_web.py
# Open http://localhost:5001 in your browser
```

## 📁 Project Structure

```
OCR Compression/
├── src/                  # Source code (Python package)
│   ├── compression/      # Core compression modules
│   │   ├── ocr_compression.py    # OCR compression engine
│   │   ├── pdf_converter.py     # PDF conversion engine
│   │   └── pipeline.py           # Main processing pipeline
│   ├── utils/            # Utility modules
│   │   ├── file_discovery.py    # File discovery system
│   │   ├── metrics.py            # Metrics calculation
│   │   ├── token_estimation.py   # Token estimation
│   │   └── deepseek_insights.py  # DeepSeek-OCR insights
│   ├── web/              # Web portal
│   │   ├── app.py                # Flask application
│   │   └── templates/
│   │       └── index.html        # Main UI (sakura-themed)
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
│   ├── developer/        # Developer documentation (this file)
│   ├── api/              # API documentation
│   └── design/           # Design documentation
├── .meta/                # Project management (not deployed)
│   ├── bugs/             # Bug tracking (YAML format)
│   ├── updates/          # Epics and backlogs
│   └── archive/          # Historical records
├── build/                # Build artifacts (gitignored)
├── dist/                 # Distribution packages (gitignored)
└── setup.py              # Package setup configuration
```

## 🎨 UI Theme: Sakura Design

The web portal features a beautiful **sakura (cherry blossom) theme**:

### Color Palette
- **Blossoms**: `#FFB7C5` - Primary pink
- **Petals**: `#FFE4E1` - Soft pink
- **Accent**: `#FF69B4` - Hot pink
- **Branches**: `#8B4513` - Brown
- **Gradients**: `#FFF0F5` → `#FFE4E1`

### Key Features
- **Falling Petals Animation**: Triggered on form submission
- **Rounded Edges**: 20px cards, 16px buttons, 12px inputs
- **Gradient Backgrounds**: Sakura watercolor background image
- **Smooth Transitions**: All interactions have gentle animations
- **Responsive Design**: Works on desktop and mobile

### UI Components
- Sakura-themed cards with soft shadows
- Gradient headers on all sections
- Animated progress bars with sakura colors
- Toast notifications with sakura styling
- Modal dialogs with sakura borders

## 🧪 Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pdf_converter.py -v

# Run with coverage
pytest --cov=src tests/

# Run with coverage report
pytest --cov=src --cov-report=html tests/
# Open htmlcov/index.html in browser
```

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and small

### Adding New Features

1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Write tests first**: Add tests in `tests/` directory
3. **Implement feature**: Write code following existing patterns
4. **Update documentation**: Update relevant docs in `docs/`
5. **Run tests**: Ensure all tests pass
6. **Submit PR**: Create pull request with description

## 🐛 Bug Tracking

Bugs are tracked in YAML format in the `bugs/` directory:

- Format: `BUG-XXX.yaml` where XXX is zero-padded 3-digit number
- See `bugs/README.md` for bug tracking schema
- Always update `bugs/README.md` statistics when creating/resolving bugs

### Creating a Bug

1. Check `bugs/` directory for highest BUG-XXX number
2. Create `BUG-XXX.yaml` with required fields
3. Update `bugs/README.md` statistics
4. Set status to `open` or `in-progress`

## 📚 Documentation Structure

### Core Documentation
- **README.md**: Quick start and overview
- **DEVELOPER.md**: This file - developer guide
- **NOTES.MD**: High-level project overview
- **CANON.md**: Immutable project rules

### Detailed Documentation
- **docs/USAGE_GUIDE.md**: Complete usage guide
- **docs/API.md**: API documentation
- **docs/developer/SMART_CONCATENATION.md**: Smart concatenation system documentation
- **docs/UI_IMPLEMENTATION.md**: UI component details
- **docs/TROUBLESHOOTING.md**: Common issues and solutions
- **docs/SOP.md**: Standard operating procedures

### Design Documentation
- **PROJECT_DESIGN_RULEBOOK.md**: Single source of truth for design
- **docs/UI_IMPLEMENTATION.md**: UI component reference (legacy)

## 🔧 Key Technologies

### Backend
- **Python 3.8+**: Core language
- **Flask**: Web framework
- **reportlab**: PDF generation
- **Pillow**: Image processing
- **tiktoken**: Token counting

### Frontend
- **HTML5/CSS3**: Structure and styling
- **Tailwind CSS**: Utility-first CSS framework
- **Vanilla JavaScript**: No frameworks, pure JS
- **Google Fonts**: Dancing Script for haiku

### Testing
- **pytest**: Testing framework
- **coverage**: Code coverage tool

## 🎯 Common Development Tasks

### Adding a New File Type Handler

1. Edit `src/compression/pdf_converter.py`
2. Add handler function following existing pattern
3. Register in `_get_handler()` method
4. Add test in `tests/test_pdf_converter.py`

### Modifying UI Theme

1. Edit `src/web/templates/index.html`
2. Update CSS variables in `:root` section
3. Modify component classes
4. Test in browser at http://localhost:5000

### Adding API Endpoint

1. Edit `src/web/app.py`
2. Add route handler
3. Update `docs/API.md`
4. Test with curl or Postman

### Updating Documentation

1. Identify correct file (see Documentation Structure above)
2. Update content
3. Update `notes.yaml` if adding new file
4. Commit with descriptive message

## 🚨 Important Notes

### UI Theme Customization

The sakura theme is implemented with:
- CSS custom properties (variables) in `:root`
- Reusable CSS classes (`.sakura-card`, `.sakura-header`, etc.)
- Inline styles for dynamic elements
- Google Fonts for typography

**To modify colors**: Update CSS variables in `index.html` `<style>` section

**To remove haiku**: Delete the section marked `<!-- HAIKU SECTION -->` in `index.html`

### Testing Requirements

- All new features must have tests
- Aim for >80% code coverage
- Test edge cases and error conditions
- Integration tests for pipeline

### Code Review Checklist

- [ ] Tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No console errors/warnings
- [ ] UI tested in browser
- [ ] Bug tracking updated if applicable

## 📞 Getting Help

- **Documentation**: Check `docs/` directory
- **Bugs**: See `bugs/README.md` for tracking
- **Design Questions**: See `PROJECT_DESIGN_RULEBOOK.md`
- **API Questions**: See `docs/API.md`

## 🎉 Contributing

Contributions are welcome! Please:

1. Follow the development workflow above
2. Write clear commit messages
3. Update relevant documentation
4. Ensure all tests pass
5. Submit PR with description

## 📝 Recent Changes

### 2025-01-16: Smart Concatenation & PDF Generation Fix
- **Smart Concatenation System**: Implemented intelligent file grouping into max 10 PDFs
  - Prioritized roll-up strategy for complex directory structures
  - Key folder identification and preservation
  - Root files handling
  - See `docs/developer/SMART_CONCATENATION.md` for full documentation
- **Critical Bug Fix**: Fixed XML/HTML escaping in PDF generation
  - Problem: reportlab Paragraph parser failed on unescaped `<`, `>`, `&` characters
  - Impact: 99/109 files failing (9.2% success rate)
  - Solution: Proper HTML entity escaping with preservation of existing entities
  - Result: 100% success rate, all files convert successfully
- **Documentation**: Added comprehensive technical documentation for smart concatenation

### 2025-01-15: Sakura UI Theme
- Added beautiful sakura (cherry blossom) theme
- Implemented falling petals animation
- Added haiku at top of page
- Updated all UI components with sakura colors
- Rounded edges and gradient backgrounds

### 2025-01-15: Complete System
- All 10 stories implemented
- Comprehensive test suite
- Full documentation
- Web portal with modern UI
- Token estimation and metrics

---

**Happy Coding! 🌸**

