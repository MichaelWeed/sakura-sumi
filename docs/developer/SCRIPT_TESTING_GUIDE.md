# Script Testing Guide

## Why This Guide Exists

When creating or modifying shell scripts, it's essential to verify they actually work before committing them. This guide helps prevent committing broken scripts that fail when users try to use them.

## The Problem We're Solving

**What happened:** A script was created to fix a missing file error, but it wasn't tested. When users tried to run it, it failed because:
- Dependencies weren't checked
- Error handling was missing
- The script assumed everything was set up correctly

**Impact:** Users encountered errors instead of a working solution.

## Testing Checklist

Before committing any script, verify:

### 1. Syntax Validation
```bash
# Check shell script syntax
bash -n scripts/your_script.sh
```

**Why:** Catches syntax errors before runtime.

### 2. Dependency Checks
```bash
# Test if the script handles missing dependencies
# Remove venv temporarily and test
mv venv venv.backup
./scripts/your_script.sh
# Should show helpful error, not crash
mv venv.backup venv
```

**Why:** Users may not have dependencies installed. Scripts should fail gracefully with clear messages.

### 3. Path Handling
```bash
# Test with different path scenarios
./scripts/your_script.sh "/absolute/path"
./scripts/your_script.sh "relative/path"
./scripts/your_script.sh  # No argument (should handle default)
```

**Why:** Scripts are often called from different contexts (Finder, terminal, Automator).

### 4. Error Conditions
```bash
# Test error cases
./scripts/your_script.sh "/nonexistent/path"  # Should error gracefully
./scripts/your_script.sh "/path/to/file.txt"  # Should handle non-directory
```

**Why:** Real-world usage includes edge cases. Handle them explicitly.

### 5. Virtual Environment Handling
```bash
# Test with and without venv
# With venv
./scripts/your_script.sh

# Without venv (rename it)
mv venv venv.backup
./scripts/your_script.sh  # Should still work or fail clearly
mv venv.backup venv
```

**Why:** Not all users have venv set up. Scripts should work or explain what's needed.

## Best Practices

### Always Include Error Handling

```bash
set -e  # Exit on error
# OR handle errors explicitly:
if ! command; then
    echo "Error: command failed" >&2
    exit 1
fi
```

**Why:** Prevents scripts from continuing after failures, which can cause confusing errors.

### Check Prerequisites

```bash
# Check if required tools exist
if ! command -v python3 >/dev/null; then
    echo "Error: python3 not found" >&2
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import required_module" 2>/dev/null; then
    echo "Error: Missing dependency. Run: pip install required_module" >&2
    exit 1
fi
```

**Why:** Provides actionable error messages instead of cryptic Python import errors.

### Validate Inputs

```bash
# Check if argument is a directory
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Not a directory: $SOURCE_DIR" >&2
    exit 1
fi
```

**Why:** Prevents confusing errors when users pass wrong arguments.

### Use Absolute Paths

```bash
# Resolve paths to avoid issues with relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
```

**Why:** Scripts are called from various locations. Absolute paths prevent path-related failures.

### Provide Clear Error Messages

```bash
# Good: Clear, actionable error
echo "Error: Dependencies not installed. Run: pip install -r requirements.txt" >&2

# Bad: Cryptic error
# (Just letting Python's import error show)
```

**Why:** Users need to know what went wrong and how to fix it.

## Testing Workflow

1. **Write the script**
2. **Check syntax**: `bash -n script.sh`
3. **Test happy path**: Run with valid inputs
4. **Test error cases**: Missing deps, wrong paths, etc.
5. **Test in different contexts**: Terminal, Automator, etc.
6. **Only then commit**

## Quick Test Command

For a new script, run this before committing:

```bash
# Syntax check
bash -n scripts/new_script.sh

# Test with a real directory (if applicable)
./scripts/new_script.sh "/tmp/test" 2>&1 | head -20

# Check exit codes
./scripts/new_script.sh "/nonexistent" && echo "ERROR: Should have failed!" || echo "OK: Failed as expected"
```

## Common Mistakes to Avoid

1. **Assuming venv exists**: Always check and handle missing venv
2. **Not checking dependencies**: Verify Python packages are installed
3. **Ignoring error codes**: Use `set -e` or check `$?`
4. **Relative paths**: Always resolve to absolute paths
5. **No input validation**: Check arguments before using them
6. **Cryptic errors**: Provide helpful error messages

## Remember

**A script that doesn't work is worse than no script at all** - it wastes users' time and creates frustration. Always test before committing.
