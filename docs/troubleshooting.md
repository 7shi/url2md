# Troubleshooting Guide

This document provides solutions to common issues encountered when working with url2md.

## Common Issues

### 1. Cache Not Found
**Problem**: Commands fail with cache directory not found errors.
**Solution**: Run `uv run url2md init` to initialize cache directory before other commands.

### 2. Import Errors
**Problem**: Python modules not found when running commands.
**Solution**: Ensure using `uv run` instead of direct Python execution.

### 3. Missing Dependencies
**Problem**: ModuleNotFoundError for required packages.
**Solution**: Check `pyproject.toml` and run `uv sync` to install dependencies.

### 4. API Errors
**Problem**: Gemini API calls failing.
**Solution**: Verify `GEMINI_API_KEY` environment variable is set correctly.

### 5. Playwright Issues
**Problem**: Dynamic rendering fails with browser errors.
**Solution**: Run `uv run playwright install` to install browser support.

### 6. Test Failures
**Problem**: Tests fail with unclear error messages.
**Solution**: Run `uv run pytest -v` to see detailed test output and error messages.

### 7. Tool Not Updated
**Problem**: Code changes not reflected after installation.
**Solution**: After code changes, use `uv cache clean url2md` before `uv tool install .` to ensure latest version.

## Debugging Tips

### Logging and Debugging
- Use `print()` statements for user-facing progress information
- Commands include progress bars using `tqdm`
- Error messages should be clear and actionable
- Full stack traces are enabled by default for debugging during development

### Shell Commands
- **Directory Changes**: When changing directories in shell commands, use subshells with parentheses `()` to avoid affecting the current shell's working directory:
  ```bash
  # Correct - uses subshell, directory change doesn't persist
  (cd tmp/test_dir && uv run pytest)
  
  # Avoid - changes current shell's directory
  cd tmp/test_dir && uv run pytest
  ```

## Getting Help

If you encounter issues not covered here:
1. Check the [README.md](../README.md) for basic usage
2. Review [CLAUDE.md](../CLAUDE.md) for development guidelines
3. Examine the test suite for examples of expected behavior
4. Enable verbose logging to identify the specific failure point