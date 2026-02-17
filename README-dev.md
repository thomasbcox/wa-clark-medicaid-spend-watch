# Developer Guide: Python Environment Setup

This project uses a project-local virtual environment to ensure reliable execution on macOS (especially with Homebrew Python and PEP 668).

## Prerequisites

- macOS with Homebrew installed.
- Python 3.12 or higher.

## Initial Setup

1. **Create the virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

2. **Activate the environment**:
   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Daily Usage

### Activation

Always work within the activated virtual environment:
```bash
source .venv/bin/activate
```

### Running Entry Points

Run scripts or servers using the python interpreter in the virtual environment:
```bash
python path/to/script.py
```

### Deactivation

To exit the virtual environment:
```bash
deactivate
```

## Troubleshooting

If you encounter "externally-managed-environment" errors, it means you are likely trying to use the global Homebrew Python. Ensure you have activated the `.venv` or are using `./.venv/bin/python` directly.
