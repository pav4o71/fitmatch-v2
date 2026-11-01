# FitMatch

FitMatch estimates your upper-body measurements from a single photo and recommends a clothing size for a chosen brand.

1. Upload (or take) a photo and enter your real height.
2. MediaPipe Pose Landmarker locates your body landmarks and estimates shoulder width and chest circumference.
3. The estimate is matched against the brand's men's tops chart (H&M, Zara, Uniqlo).
4. If you are within 1.5 cm of a size edge, you get a boundary warning (e.g. "size up for a looser fit").

If the ankles are visible, height is scaled from nose to ankle (higher accuracy). Otherwise it falls back to nose-to-hip scaled by a 47% body ratio (medium accuracy).

## Tech stack

- Python 3.13
- MediaPipe Tasks API (`PoseLandmarker`, heavy model) and OpenCV (headless)
- Streamlit frontend

## Project structure

```
app.py                     Streamlit wizard UI (setup, pose guide, capture, results)
src/body_profiler.py       Photo -> {"shoulder_cm", "chest_cm"} with a pose quality gate
src/size_matcher.py        Brand size charts and boundary-warning logic
assets/                    pose_landmarker_heavy.task model, style.css, pose_guide.png
.streamlit/config.toml     Theme
tests/                     pytest suite
test_photo.jpg.JPG         Sample photo used by the tests
packages.txt               Linux system packages for Streamlit Cloud
requirements.txt           Python dependencies
```

## Run locally

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with `python -m pytest tests`.

## Notes

Zara and Uniqlo charts come from third-party sources (converted from inches) and XS is extrapolated; verify against each brand's size guide. Measurements are estimates, not tailoring-grade.
