# Code Review Checklist

## Purpose

This checklist helps catch issues before code is committed. Use it when reviewing your own code or code from AI assistants.

## What Went Wrong (Example)

**The Issue:** A shell script was created to fix a missing file error, but it wasn't tested. When users tried to run it, they got cryptic Python import errors instead of helpful messages.

**Root Cause:** The script assumed:
- Dependencies were already installed
- Virtual environment was set up correctly
- Everything would work as expected

**Reality:** Users often don't have everything set up, and scripts need to handle that gracefully.

## Pre-Commit Checklist

### For Shell Scripts

- [ ] **Syntax check**: Run `bash -n script.sh` - catches syntax errors
- [ ] **Test with missing dependencies**: Temporarily remove venv, test error handling
- [ ] **Test with invalid inputs**: Wrong paths, missing files, etc.
- [ ] **Test in different contexts**: Terminal, Automator, right-click from Finder
- [ ] **Error messages are helpful**: Users should know what went wrong and how to fix it
- [ ] **Exit codes are correct**: Script should exit with proper codes for success/failure

### For Python Code

- [ ] **Import errors handled**: What happens if dependencies are missing?
- [ ] **File paths validated**: Check if files/directories exist before using them
- [ ] **Error messages are user-friendly**: Not just stack traces
- [ ] **Edge cases considered**: Empty inputs, None values, etc.

### For Any Code

- [ ] **Actually test it**: Don't just write it and commit
- [ ] **Test the happy path**: Does it work when everything is correct?
- [ ] **Test error cases**: What happens when things go wrong?
- [ ] **Check error messages**: Are they helpful to users?
- [ ] **Verify it solves the problem**: Does it actually fix what it claims to fix?

## Quick Test Commands

### Shell Scripts
```bash
# Syntax check
bash -n scripts/your_script.sh

# Test with real input
./scripts/your_script.sh "/tmp/test"

# Test error case
./scripts/your_script.sh "/nonexistent"  # Should error gracefully
```

### Python Scripts
```bash
# Test help/usage
python scripts/your_script.py --help

# Test with missing dependencies (if possible)
# Temporarily rename venv and test error handling
```

## Red Flags

Watch out for these signs that code might not be ready:

1. **No error handling**: Code assumes everything will work
2. **Cryptic error messages**: Users see stack traces instead of helpful messages
3. **No input validation**: Code doesn't check if inputs are valid
4. **Hardcoded assumptions**: "This will always exist" or "User will always have X"
5. **Not tested**: "It should work" but hasn't been verified

## The Golden Rule

**If you didn't test it, don't commit it.**

Even if you're confident it will work, test it. Real-world usage is different from what you expect.

## For AI-Generated Code

When reviewing code from AI assistants:

1. **Don't trust, verify**: AI can make mistakes or miss edge cases
2. **Test it yourself**: Run the code in your environment
3. **Check error handling**: Does it fail gracefully?
4. **Verify it solves the problem**: Does it actually do what you asked?
5. **Look for assumptions**: What does the code assume that might not be true?

## Remember

**Broken code is worse than no code.** It wastes time, creates frustration, and erodes trust. A few minutes of testing saves hours of debugging later.
