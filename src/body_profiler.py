import cv2
import math
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from pathlib import Path
from typing import Dict, Any

DEFAULT_MODEL_PATH = str(Path(__file__).resolve().parent.parent / "assets" / "pose_landmarker_heavy.task")

# Pose landmark indices (same as the legacy PoseLandmark enum)
NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, LEFT_ANKLE = 0, 11, 12, 23, 27

class BodyProfiler:
    def __init__(self, model_path: str = DEFAULT_MODEL_PATH) -> None:
        options = vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.IMAGE,
            min_pose_detection_confidence=0.6
        )
        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def calculate_distance(self, point1: Any, point2: Any, image_width: int, image_height: int) -> float:
        """Calculates pixel distance between two MediaPipe normalized landmarks."""
        x1, y1 = point1.x * image_width, point1.y * image_height
        x2, y2 = point2.x * image_width, point2.y * image_height
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def extract_measurements(self, image_path: str, real_height_cm: float) -> Dict[str, float]:
        """Analyzes a photo and estimates body measurements with a smart fallback."""

        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Could not find image at {image_path}")

        image_height, image_width, _ = image.shape
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        results = self.landmarker.detect(mp_image)

        if not results.pose_landmarks:
            raise ValueError("No human body detected. Please use a clearer photo.")

        landmarks = results.pose_landmarks[0]
        nose = landmarks[NOSE]
        left_ankle = landmarks[LEFT_ANKLE]
        left_hip = landmarks[LEFT_HIP]

        # SMART FALLBACK LOGIC
        if left_ankle.visibility > 0.5 and left_ankle.y < 0.98:
            print("[System] Ankle detected! Using Full Body calculation (High Accuracy).")
            pixel_height = self.calculate_distance(nose, left_ankle, image_width, image_height)
            adjusted_pixel_height = pixel_height * 1.10
            cm_per_pixel = real_height_cm / adjusted_pixel_height
        else:
            print("[System] Ankle cut off. Falling back to Hip calculation (Medium Accuracy).")
            pixel_height = self.calculate_distance(nose, left_hip, image_width, image_height)
            adjusted_pixel_height = pixel_height * 1.15
            cm_per_pixel = (real_height_cm * 0.47) / adjusted_pixel_height

        # Calculate Shoulders & Chest
        left_shoulder = landmarks[LEFT_SHOULDER]
        right_shoulder = landmarks[RIGHT_SHOULDER]

        shoulder_width_pixels = self.calculate_distance(left_shoulder, right_shoulder, image_width, image_height)
        shoulder_width_cm = shoulder_width_pixels * cm_per_pixel
        estimated_chest_circumference = (shoulder_width_cm * 0.9) * math.pi

        return {
            "shoulder_cm": round(shoulder_width_cm, 1),
            "chest_cm": round(estimated_chest_circumference, 1)
        }

if __name__ == "__main__":
    profiler = BodyProfiler()
    try:
        my_height_cm = 180.0  # Note: Edit this to my actual height if necessary
        test_image = str(Path(__file__).resolve().parent.parent / "test_photo.jpg.JPG")

        measurements = profiler.extract_measurements(test_image, my_height_cm)

        print("\n--- AI Measurement Extraction Successful ---")
        print(f"Shoulder Width: {measurements['shoulder_cm']} cm")
        print(f"Chest Circumference (Est): {measurements['chest_cm']} cm")
    except Exception as e:
        print(f"Error: {e}")
