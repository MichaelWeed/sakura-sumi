# Quick Action Setup Guide

## Problem: Quick Action Does Nothing

If your Quick Action appears to do nothing when you right-click on a folder, follow these steps:

## Step 1: Verify Automator Configuration

1. Open **Automator** (Applications > Automator)
2. Find your "Compress with Sakura Sumi" Quick Action
3. Check the **"Run Shell Script"** action:
   - **Shell:** `/bin/bash`
   - **Pass input:** `as arguments` (CRITICAL - must be set to "as arguments")
   - **Script:** Should contain:
     ```bash
     /Users/johndoe/Projects/Sakura\ Sumi/scripts/compress_with_defaults.sh "$@"
     ```
     OR if using relative path:
     ```bash
     cd "/Users/johndoe/Projects/Sakura Sumi"
     ./scripts/compress_with_defaults.sh "$@"
     ```

## Step 2: Check for Log File

The script now creates a log file you can check:

```bash
# Check the most recent log
tail -50 ~/Library/Logs/sakura-sumi-quick-action.log

# Or check if it exists
ls -la ~/Library/Logs/sakura-sumi-quick-action.log
```

## Step 3: Test the Script Directly

Run the script from Terminal to verify it works:

```bash
/Users/johndoe/Projects/Sakura\ Sumi/scripts/compress_with_defaults.sh '/Users/johndoe/Downloads/your-folder-name'
```

If this works but the Quick Action doesn't, the issue is with Automator configuration.

## Step 4: Common Issues

### Issue: "Pass input" is set to "to stdin" instead of "as arguments"
**Fix:** Change "Pass input" dropdown to "as arguments"

### Issue: Script path has spaces and isn't quoted
**Fix:** Use the full path with escaped spaces:
```bash
/Users/johndoe/Projects/Sakura\ Sumi/scripts/compress_with_defaults.sh "$@"
```

### Issue: Quick Action doesn't have permission to run
**Fix:** 
1. Go to System Settings > Privacy & Security
2. Check if Automator needs permission
3. Try running the Quick Action again and approve any permission prompts

### Issue: Output directory permission denied
**Fix:** The script now detects this and shows a clear error. Make sure you're selecting a project folder, not your home directory.

## Step 5: Create a New Quick Action (If Needed)

If the existing one doesn't work, create a new one:

1. Open **Automator**
2. Choose **Quick Action**
3. Set:
   - **Workflow receives:** `folders` in `Finder`
   - **Input receives:** `any folder`
4. Add **"Run Shell Script"** action:
   - **Shell:** `/bin/bash`
   - **Pass input:** `as arguments`
   - **Script:**
     ```bash
     /Users/johndoe/Projects/Sakura\ Sumi/scripts/compress_with_defaults.sh "$@"
     ```
5. Save as "Compress with Sakura Sumi"

## Verification

After setup, when you right-click on a folder:
1. You should see "Compress with Sakura Sumi" in the Quick Actions menu
2. Clicking it should show output (or create a log file)
3. After completion, you should see a new folder: `{your-folder-name}_ocr_ready`

## Still Not Working?

1. Check the log file: `~/Library/Logs/sakura-sumi-quick-action.log`
2. Try running from Terminal to see actual error messages
3. Verify the script is executable: `chmod +x /Users/johndoe/Projects/Sakura\ Sumi/scripts/compress_with_defaults.sh`
