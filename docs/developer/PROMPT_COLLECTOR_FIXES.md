# Prompt Collector Fixes - Implementation Summary

## Issues Addressed

### 1. Warning Message UX (FIXED)
**Problem**: Warning messages appeared without action buttons, leaving users unsure what to do.

**Solution**:
- Added "Proceed Anyway" and "Go Back" buttons to warning/error recommendations
- Buttons appear conditionally when `severity === 'warning'` or `severity === 'error'`
- "Go Back" button preserves all user data (prompts, form inputs) and returns to form
- "Proceed Anyway" button confirms the user wants to continue despite the warning

**Implementation**:
- Modified `displayTokenEstimation()` to add action buttons to recommendation display
- Added button handlers that:
  - Store recommendation state in `window.currentRecommendation`
  - Block form submission until user confirms
  - Allow going back without losing any data

### 2. Token Count Mismatch (FIXED)
**Problem**: Drawer showed approximate token count (~120k) but actual estimation showed different value (31.5k).

**Solution**:
- Added "Estimate Tokens" button to prompt drawer
- Button calls `/api/estimate` with `prompt_payload` to get accurate token counts
- Updated prompt stats to show approximate token count (chars / 4) in drawer
- Estimation results displayed in main view's token estimation panel

**Implementation**:
- Extended `/api/estimate` endpoint to accept `prompt_payload` array
- Creates temporary workspace, runs file discovery, calculates accurate tokens
- Added `promptEstimateBtn` event handler that:
  - Sends prompts to estimation endpoint
  - Displays results in main token estimation panel
  - Shows accurate token counts before compression

### 3. Compression Artifacts Testing (ADDED)
**Problem**: Need a way to test for compression artifacts in generated PDFs.

**Solution**:
- Created `tests/test_compression_artifacts.py` script
- Generates a test image with various symbols:
  - ASCII/Unicode text
  - Mathematical symbols
  - Emojis and special characters
  - Geometric shapes (circles, squares, lines)
  - Varying line thicknesses

**Usage**:
```bash
python tests/test_compression_artifacts.py
# Generates symbol_sample.png
# Compress and compare for artifacts
```

## Technical Details

### Recommendation Button Flow
1. User submits form (directory or prompts)
2. Estimates are calculated and returned
3. If recommendation has warning/error severity:
   - Display recommendation with action buttons
   - Block further submission attempts
   - Wait for user to click "Proceed Anyway" or "Go Back"
4. If "Go Back" clicked:
   - Hide progress view
   - Show form again
   - Clear recommendation display
   - Preserve all user data
5. If "Proceed Anyway" clicked:
   - Set `window.recommendationConfirmed = true`
   - Re-submit the form data
   - Continue with compression

### Token Estimation for Prompts
- `/api/estimate` now accepts `prompt_payload` array
- Creates temporary workspace using `build_prompt_workspace()`
- Runs standard file discovery and token estimation
- Cleans up temporary files after estimation
- Returns same format as directory estimation

### Data Preservation
- Prompt data stored in `PromptCollectorStore` (in-memory, persists during session)
- Form inputs preserved when going back
- No data loss when user clicks "Go Back"

## Files Modified

1. `src/web/templates/index.html`:
   - Added recommendation action buttons
   - Added "Estimate Tokens" button to prompt drawer
   - Updated token display in prompt stats
   - Modified form submission to check recommendations
   - Added "Go Back" functionality

2. `src/web/app.py`:
   - Extended `/api/estimate` to handle `prompt_payload`
   - Added temporary workspace creation/cleanup for prompt estimation

3. `tests/test_compression_artifacts.py`:
   - New test script for compression artifact testing

## Future Enhancements

- Consider adding job cancellation when user clicks "Go Back" after job starts
- Add export/import functionality for prompt sets (hooks already exposed via `PromptCollectorStore`)
- Consider showing estimates automatically when prompts are added (debounced)

