# 🏗️ FITMATCH TECHNICAL BLUEPRINT

## DIRECTORY STRUCTURE
Ensure the final project matches this structure exactly. Create folders and move files as necessary:
/fitmatch-v2
  ├── /src
  │    ├── __init__.py
  │    ├── body_profiler.py (MediaPipe vision logic)
  │    └── size_matcher.py (Dictionaries & comparison logic)
  ├── /assets (Store the downloaded .task model here)
  ├── app.py (Streamlit frontend UI)
  ├── requirements.txt
  ├── CLAUDE_AUTO_PROMPT.md
  └── APP_ARCHITECTURE.md

## COMPONENT REQUIREMENTS

### 1. `src/body_profiler.py`
*   Must continue using the modern `mediapipe.tasks` `PoseLandmarker` API.
*   Must retain the "Smart Fallback" logic (Ankle visibility > 0.5 = Full Body. Otherwise, use Hip calculation with 47% ratio).
*   Must return a clean dictionary: `{"shoulder_cm": X, "chest_cm": Y}`.

### 2. `src/size_matcher.py`
*   Must contain a multi-brand dictionary containing at minimum: **H&M, Zara, and Uniqlo**.
*   Must include the "Boundary Warning" logic: If the user's estimated chest size is within 1.5 cm of the lower or upper bound of their recommended size, return a warning flag (e.g., `{"size": "L", "boundary_warning": "You are very close to an XL. For a looser fit, size up."}`).

### 3. `app.py` (Streamlit Frontend)
*   **Design:** Use Streamlit's `st.set_page_config` for a wide layout and custom title.
*   **Inputs:** 
    *   `st.camera_input` OR `st.file_uploader` for the user's photo.
    *   `st.slider` for the user's real height in cm.
    *   `st.selectbox` for the target clothing brand.
*   **Processing State:** Use `st.spinner` while the MediaPipe model runs.
*   **Output:** Use `st.success` and `st.metric` to display the final chest measurement and the recommended size boldly. Show the boundary warning as an `st.info` or `st.warning` box if triggered.