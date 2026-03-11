# Validation Process

## Why This Document Exists

Code should be validated before committing. This document outlines how to verify that scripts and features actually work.

## The Problem

**What happened:** A script was created and committed without being tested. While the script had good error handling, it wasn't verified to work end-to-end.

**Impact:** Users encountered issues that could have been caught with proper validation.

## Validation Workflow

### For Shell Scripts

**Step 1: Syntax Check**
```bash
bash -n scripts/your_script.sh
```
**Why:** Catches syntax errors immediately.

**Step 2: Test Error Cases**
```bash
# Test with missing dependencies
./scripts/your_script.sh /tmp/test_dir
# Should show helpful error, not crash
```

**Step 3: Install Dependencies and Test Success Path**
```bash
# Set up environment
source venv/bin/activate
pip install -r requirements.txt

# Test the script actually works
./scripts/your_script.sh /tmp/test_dir
# Should complete successfully
```

**Step 4: Verify Output**
```bash
# Check that expected output was created
ls -la /tmp/test_dir_ocr_ready/
# Should see PDF files
```

### For Python Code

**Step 1: Import Check**
```bash
python3 -c "from src.main import main; print('✓ Imports work')"
```

**Step 2: Help/Usage Check**
```bash
python3 scripts/compress.py --help
# Should show usage without errors
```

**Step 3: Dry Run**
```bash
# Test with a small directory
python3 scripts/compress.py /tmp/test_dir -v
# Should complete successfully
```

**Step 4: Verify Output**
```bash
# Check output directory exists and has files
ls -la /tmp/test_dir_ocr_ready/
```

## Complete Validation Checklist

Before committing any code:

- [ ] **Syntax is valid**: Scripts parse without errors
- [ ] **Dependencies checked**: Code handles missing dependencies gracefully
- [ ] **Error cases tested**: Wrong inputs, missing files, etc.
- [ ] **Success path tested**: Code works when everything is correct
- [ ] **Output verified**: Expected files/behavior actually happens
- [ ] **Error messages are helpful**: Users know what went wrong and how to fix it

## Quick Validation Command

For scripts, run this before committing:

```bash
# 1. Syntax
bash -n scripts/your_script.sh || exit 1

# 2. Test error case (missing deps)
./scripts/your_script.sh /tmp/test 2>&1 | grep -q "dependencies" && echo "✓ Error handling works"

# 3. Install deps and test success
source venv/bin/activate
pip install -q -r requirements.txt
./scripts/your_script.sh /tmp/test && echo "✓ Success path works"
deactivate
```

## What "Working" Means

A script "works" when:
1. It handles errors gracefully (doesn't crash)
2. It provides helpful error messages
3. It completes successfully when conditions are met
4. It produces the expected output

**Just having good error messages isn't enough** - the script must also work when everything is set up correctly.

## Remember

**Test the full workflow, not just error cases.** A script that only fails gracefully but never succeeds is still broken.

## What I Learned

When creating the `compress_with_defaults.sh` script:
- ✅ I added error handling (good!)
- ✅ I checked for dependencies (good!)
- ❌ I didn't test the success path (bad!)
- ❌ I didn't verify the script actually works end-to-end (bad!)

**The fix:** Always test both error cases AND success cases. A script that only fails gracefully is still broken if it doesn't work when everything is set up correctly.
