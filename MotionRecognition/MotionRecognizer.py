import mediapipe

from MotionRecognition.utils.dataset_utils import load_dataset, load_reference_signs
from MotionRecognition.utils.mediapipe_utils import mediapipe_detection
from MotionRecognition.sign_recorder import SignRecorder


class MotionRecognizer:
    def __init__(self, cap):
        try:
            # Create dataset of the videos where landmarks have not been extracted yet
            videos = load_dataset()

            # Create a DataFrame of reference signs (name: str, model: SignModel, distance: int)
            reference_signs = load_reference_signs(videos)

            # Object that stores mediapipe results and computes sign similarities
            self.sign_recorder = SignRecorder(reference_signs)

            self.holistic = mediapipe.solutions.holistic.Holistic(
                min_detection_confidence=0.5, min_tracking_confidence=0.5
            )

            self.cap = cap
        except Exception as e:
            print(f"Failed to initialize motion recognizer: {e}")

    def analyze(self, frame):
        try:
            # Make detections
            image, results = mediapipe_detection(frame, self.holistic)

            # Process results
            sign_detected = self.sign_recorder.recognize(results)

            return sign_detected
        except Exception as e:
            print(f"Failed to recognize motion: {e}")

    def start_motion(self):
        self.sign_recorder.record()

    def is_recording(self):
        return self.sign_recorder.is_recording
