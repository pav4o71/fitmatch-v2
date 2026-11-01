# 🤖 CLAUDE AUTONOMOUS EXECUTION MASTER PLAN

## CORE DIRECTIVE
You are operating in FULLY AUTONOMOUS MODE. Your goal is to build, test, and finalize the "FitMatch" Streamlit application. You are authorized to make executive engineering decisions, search the web, read official documentation, audit code, and run terminal commands without asking for user permission. 

Do not stop until the Streamlit app is fully functional. Only pause to ask the user if you strictly require a private password, paid API key, or physical real-world action.

## 🛠️ STRATEGY & FAILSAFES (PREVENTING FAILURE)
1. **Pre-flight Check:** Before writing code, verify you are in the `fitmatch-v2` directory and the Python virtual environment `(venv)` is strictly active. If not, activate it. Check that Python 3.13 is running.
2. **Command Verification:** Always check the output of your terminal commands. If a package fails to install, search for the correct Python 3.13 compatible wheel or alternative library.
3. **The 3-Strike Pivot Rule:** If any script, web scraper, or command fails 3 times in a row, DO NOT keep trying the same approach. Pivot immediately to a valid alternative (e.g., if scraping Zara fails 3 times, search GitHub/Reddit for the raw JSON/sizing data instead).
4. **Information Gathering:** If you forget a MediaPipe Tasks API syntax or Streamlit component, use your browser/search tools to read the official docs immediately. Do not guess.

## 📋 TASK LIST (EXECUTE IN ORDER)
1. **Audit:** Read the existing `body_profiler.py` and `size_matcher.py` to understand the current logic (MediaPipe Tasks API, smart fallback, and H&M dictionary).
2. **Refactor & Structure:** Reorganize the code according to `APP_ARCHITECTURE.md`.
3. **Data Expansion:** Use your browser/search tools to find Men's Top sizing charts (Chest cm) for **Zara** and **Uniqlo**. Add them to the sizing dictionary.
4. **Web UI Construction:** Install `streamlit` and build `app.py`. Implement photo upload, brand selection, height slider, and the "Boundary Warning" logic (alerting users if they are within 1.5 cm of a size edge).
5. **Testing:** Write a quick unit test script. Run the app silently in the background, send a test payload, and verify it doesn't crash.
6. **Handoff:** Generate a clean `requirements.txt`. Print a massive success message to the terminal with the exact command the user needs to run (`streamlit run app.py`).