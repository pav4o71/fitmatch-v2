# FitMatch Project Rules

**Stack:** Python Backend, FastAPI, Next.js Frontend.

**Goal:** AI Body measurement extraction and sizing recommendation.

## Environment (CRITICAL)
We are on Windows using PowerShell. You must ALWAYS verify if the (venv) virtual environment is active before running any Python or pip commands. If it is not active, you must activate it using `.\venv\Scripts\Activate.ps1`.

## Google Drive Integration
Code files (.py, .js) remain local. Project documentation, architecture logs, and test image assets should be referenced from or saved to the connected Google Drive project folder when appropriate.

## Rules
- Keep Python files strictly under 200 lines.
- Name files explicitly based on their utility (e.g., `body_profiler.py`).
- Use type hints for all Python functions.
- Never overwrite venv or dependency files without asking.
