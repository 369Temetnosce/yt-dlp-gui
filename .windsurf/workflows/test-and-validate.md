# /test-and-validate

Run tests and validate code quality for the yt-dlp GUI project.

## Description

This workflow runs the test suite, checks code quality, and validates the application.

## Workflow Steps

### Step 1: Run Unit Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

Report any failures with details.

### Step 2: Run Linting

```bash
# Check code style
flake8 src/ tests/
# Or with ruff (faster)
ruff check src/ tests/
```

### Step 3: Type Checking

```bash
mypy src/ --ignore-missing-imports
```

### Step 4: Test UI Manually (if applicable)

1. Launch the application: `python src/main.py`
2. Test the specific feature
3. Verify no UI freezing during downloads

### Step 5: Build Test

```bash
# Test PyInstaller build
pyinstaller --onefile src/main.py --name yt-dlp-gui --windowed
```

## Success Criteria

- [ ] All unit tests pass
- [ ] No linting errors
- [ ] No type errors
- [ ] UI remains responsive
- [ ] Build completes without errors

## Usage Example

```
/test-and-validate

Run the full test suite and check for any issues.
```
