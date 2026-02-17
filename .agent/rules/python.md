# Python Environment Rule

When executing Python commands for this project, ALWAYS use the project-local virtual environment located at `./.venv`.

## Instructions for Agents

1. **Interpreter**: Use `./.venv/bin/python` for all Python script executions, tests, and REPLs.
2. **Package Manager**: Use `./.venv/bin/pip` for installing or listing packages.
3. **Avoid System Python**: Do not use the system or global Python on the PATH (e.g., `/usr/bin/python3` or `/opt/homebrew/bin/python3`) unless explicitly instructed to do so for environment setup.
4. **Terminal Sessions**: If running commands in a terminal, ensure the virtual environment is activated by running `source .venv/bin/activate` first, or use the full path to the binaries inside `.venv/bin/`.

This ensures consistency and avoids issues with "externally managed environments" on macOS.
