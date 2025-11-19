# Contributing to 🌸 Sakura Sumi

Thank you for your interest in contributing to Sakura Sumi! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate it: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Install development dependencies: `pip install pytest pytest-cov`

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose

### Testing

- Write tests for new features
- Ensure all tests pass: `pytest tests/`
- Run with coverage: `pytest --cov=src tests/`
- Aim for high test coverage on new code

### Bug Reports

- Use the bug tracking system in `bugs/` directory
- Create a new `BUG-XXX.yaml` file following the template
- Include steps to reproduce, expected vs actual behavior
- Provide environment details (OS, Python version, etc.)

### Pull Requests

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Write or update tests
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a pull request with a clear description

### Commit Messages

- Use clear, descriptive commit messages
- Reference bug numbers if applicable: `Fix BUG-XXX: description`
- Keep commits focused and atomic

## Project Structure

- `src/` - Source code
- `tests/` - Test suite
- `docs/` - Documentation
- `bugs/` - Bug tracking files
- `config/` - Configuration templates

## Questions?

Open an issue on GitHub for questions or clarifications.

