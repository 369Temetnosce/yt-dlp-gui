# /generate-feature

Implement a new feature for the yt-dlp GUI app following project standards.

## Description

This workflow guides Cascade through implementing a complete feature including code, tests, and documentation for the PyQt6 yt-dlp wrapper application.

## Prerequisites

- Feature request filled out in `FEATURE_REQUEST.md`
- Project rules reviewed in `.windsurfrules.md`
- Architecture understood from the layered design

## Workflow Steps

### Step 1: Understand Requirements

1. Read the feature request in `FEATURE_REQUEST.md`
2. Identify which layer(s) need changes (UI, Logic, Wrapper)
3. Ask clarifying questions if requirements are ambiguous

### Step 2: Review Existing Patterns

1. Check `examples/python/` for Python patterns
2. Review `.windsurfrules.md` for coding standards
3. Check existing code in `src/` for consistency

### Step 3: Create Implementation Plan

1. Identify files to create or modify
2. Plan signal/slot connections for UI changes
3. Consider threading requirements (QThread for downloads)
4. Outline test cases

### Step 4: Implement the Feature

1. Follow the layered architecture (UI → Logic → Wrapper)
2. Use PyQt6 signals for cross-thread communication
3. Add proper error handling with user-friendly messages
4. Include logging for debugging

### Step 5: Write Tests

1. Create unit tests in `tests/` folder
2. Use pytest with appropriate fixtures
3. Mock yt-dlp subprocess calls
4. Test error conditions

### Step 6: Update Documentation

1. Add docstrings to new functions
2. Update README if user-facing feature
3. Add usage examples if needed

## Success Criteria

- [ ] Feature works as described
- [ ] Follows layered architecture
- [ ] Unit tests written and passing
- [ ] No blocking of UI thread
- [ ] Error handling with user-friendly messages
- [ ] Code follows project patterns

## Usage Example

```
/generate-feature

Please implement the feature in @FEATURE_REQUEST.md
following the patterns in @.windsurfrules.md
```
