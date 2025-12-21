# /debug-issue

Debug and fix issues in the yt-dlp GUI application.

## Description

Systematic debugging workflow for PyQt6/yt-dlp issues.

## Common Issue Categories

### UI Issues
- Frozen/unresponsive UI → Check if blocking main thread
- Layout problems → Check QSS styles and layouts
- Signal not firing → Verify signal/slot connections

### Download Issues
- yt-dlp errors → Check subprocess output parsing
- Progress not updating → Verify signal emission from QThread
- File not saving → Check path handling and permissions

### Threading Issues
- Race conditions → Review QThread usage
- Crashes → Check thread-safe signal/slot usage

## Workflow Steps

### Step 1: Reproduce the Issue

1. Get exact steps to reproduce
2. Check console/log output
3. Identify error messages

### Step 2: Add Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug logging
logger.debug(f"Variable state: {variable}")
```

### Step 3: Locate Root Cause

1. Trace the code path
2. Check which layer has the bug (UI, Logic, Wrapper)
3. Verify yt-dlp command being executed

### Step 4: Implement Fix

1. Fix the root cause, not symptoms
2. Follow existing patterns
3. Add error handling if missing

### Step 5: Write Regression Test

1. Create test that catches this bug
2. Verify test fails without fix, passes with fix

### Step 6: Verify

1. Run reproduction steps - issue resolved
2. Run full test suite - no regressions

## Success Criteria

- [ ] Root cause identified
- [ ] Fix addresses root cause
- [ ] Regression test written
- [ ] All tests pass
- [ ] Issue no longer reproducible

## Usage Example

```
/debug-issue

The progress bar doesn't update during downloads.
Expected: Progress updates in real-time.
Actual: Progress stays at 0% until download completes.
```
