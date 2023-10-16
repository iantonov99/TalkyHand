# STEP 1: Imports
import os
import mediapipe as mp
from mediapipe.tasks import python
import cv2
import numpy as np
import threading
import time


# source for threading: https://stackoverflow.com/questions/76320300/nameerror-name-mp-image-is-not-defined-with-mediapipe-gesture-recognition
class GestureRecognizer:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_gestures = []
        self.save_text_mode = True
        self.current_letter = ""
        self.start_time = None
        self.saved_text = ""
        self.words_list = []

        self.cap = cv2.VideoCapture(0)

        self.CONFIDENCE_THRESHOLD = 0.75
        self.TIME_THRESHOLD = 0.75

        model_path = os.path.join("GestureRecognition", "gesture_recognizer.task")

        # STEP 2: Create the task
        GestureRecognizer = mp.tasks.vision.GestureRecognizer
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        # Create a gesture recognizer instance with the live stream mode:
        options = GestureRecognizerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_hands=2,
            result_callback=self.save_result,
        )

        self.recognizer = GestureRecognizer.create_from_options(options)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
        )
        self.timestamp = 0

    def recognize(self, image):
        image_array = np.asarray(image)

        # Convert the frame received from OpenCV to a MediaPipe’s Image object.
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_array)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Display saved text on the bottom left part of the frame
        cv2.putText(
            image,
            f"Saved Text: {self.saved_text}",
            (50, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        # display the words list on the top right part of the frame, one word per line
        y_pos = 50
        for word in self.words_list:
            cv2.putText(
                image, word, (400, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )
            y_pos += 50

        # Run the task
        self.recognizer.recognize_async(mp_image, self.timestamp)
        self.timestamp = (
            self.timestamp + 1
        )  # should be monotonically increasing, because in LIVE_STREAM mode

        self.put_gestures(image)

    def check_and_save_letter(self):
        if self.current_letter and time.time() - self.start_time >= self.TIME_THRESHOLD:
            if self.current_letter == "space":
                self.saved_text += " "
            elif self.current_letter == "del":
                self.saved_text = self.saved_text[:-1]
            elif self.current_letter == "unknown":
                pass
            else:
                self.saved_text += self.current_letter

            self.current_letter = ""
            self.start_time = None

    def get_current_text(self):
        return self.saved_text

    def reset_text(self):
        self.saved_text = ""

    def get_current_gesture(self):
        if self.current_gestures:
            return self.current_gestures[0][0]

        return None

    def put_gestures(self, frame):
        self.lock.acquire()
        gestures = self.current_gestures
        self.lock.release()
        y_pos = 50

        for hand_gesture_name, hand_gesture_score in gestures:
            cv2.putText(
                frame,
                hand_gesture_name,
                (50, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
            cv2.putText(
                frame,
                f"{hand_gesture_score:.2f}",
                (250, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
            y_pos += 50

            if self.save_text_mode and hand_gesture_name.isalpha():
                if not self.current_letter:
                    self.current_letter = hand_gesture_name
                    self.start_time = time.time()
                elif self.current_letter != hand_gesture_name:
                    self.current_letter = hand_gesture_name
                    self.start_time = time.time()
                else:
                    self.check_and_save_letter()

    def save_result(self, result, output_image, timestamp_ms):
        # print(f'gesture recognition result: {result}')
        self.lock.acquire()  # solves potential concurrency issues
        self.current_gestures = []
        if result is not None and any(result.gestures):
            # print("Recognized gestures:")
            for single_hand_gesture_data in result.gestures:
                # the gesture is added to the list only if the confidence is high enough
                if single_hand_gesture_data[0].score > self.CONFIDENCE_THRESHOLD:
                    gesture_name = (
                        single_hand_gesture_data[0].category_name,
                        single_hand_gesture_data[0].score,
                    )
                    # print(gesture_name)
                    self.current_gestures.append(gesture_name)
                else:
                    # print("Gesture not recognized with enough confidence.")
                    gesture_name = "unknown", 1 - single_hand_gesture_data[0].score
                    self.current_gestures.append(gesture_name)
        self.lock.release()

    def flip_save_text_mode(self):
        print(self.save_text_mode)
        self.save_text_mode = not self.save_text_mode

    def get_save_text_mode(self):
        return self.save_text_mode


if __name__ == "__main__":
    gesture_recognizer = GestureRecognizer()
    gesture_recognizer.main()
