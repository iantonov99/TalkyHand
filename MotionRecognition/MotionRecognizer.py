import cv2
import mediapipe

try:
    from MotionRecognition.utils.dataset_utils import load_dataset, load_reference_signs
    from MotionRecognition.utils.mediapipe_utils import mediapipe_detection
    from MotionRecognition.sign_recorder import SignRecorder
    from MotionRecognition.webcam_manager import WebcamManager
except Exception as e:
    print(f"Failed to import: {e}")


class MotionRecognizer:
    def __init__(self, cap):
        try:
            # Create dataset of the videos where landmarks have not been extracted yet
            videos = load_dataset()

            # Create a DataFrame of reference signs (name: str, model: SignModel, distance: int)
            reference_signs = load_reference_signs(videos)

            # Object that stores mediapipe results and computes sign similarities
            self.sign_recorder = SignRecorder(reference_signs)

            # Object that draws keypoints & displays results
            self.webcam_manager = WebcamManager()

            self.holistic = mediapipe.solutions.holistic.Holistic(
                min_detection_confidence=0.5, min_tracking_confidence=0.5
            )

            self.cap = cap
        except Exception as e:
            print(f"Failed to initialize motion recognizer: {e}")

        """
        # Turn on the webcam
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # Set up the Mediapipe environment
        with mediapipe.solutions.holistic.Holistic(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        ) as self.holistic:
            while cap.isOpened():

                # Read feed
                ret, frame = cap.read()

                # Make detections
                image, results = mediapipe_detection(frame, self.holistic)

                # Process results
                sign_detected, is_recording = sign_recorder.process_results(results)

                # Update the frame (draw landmarks & display result)
                webcam_manager.update(frame, results, sign_detected, is_recording)

                pressedKey = cv2.waitKey(1) & 0xFF
                if pressedKey == ord("r"):  # Record pressing r
                    sign_recorder.record()
                elif pressedKey == ord("q"):  # Break pressing q
                    break

            cap.release()
            cv2.destroyAllWindows()
            """

    def analyze(self, frame):
        try:
            # Make detections
            image, results = mediapipe_detection(frame, self.holistic)

            # Process results
            sign_detected = self.sign_recorder.recognize(results)

            # self.webcam_manager.update(frame, results, sign_detected, self.is_recording)

            return sign_detected
        except Exception as e:
            print(f"Failed to recognize motion: {e}")

    def start_motion(self):
        self.sign_recorder.record()

    def is_recording(self):
        return self.sign_recorder.is_recording
