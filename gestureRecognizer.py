# STEP 1: Imports
import mediapipe as mp
from mediapipe.tasks import python
import cv2
import numpy as np
import threading

# source for threading: https://stackoverflow.com/questions/76320300/nameerror-name-mp-image-is-not-defined-with-mediapipe-gesture-recognition
class GestureRecognizer:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_gestures = []
    
    def main(self):
        model_path = "gesture_recognizer.task"

        # STEP 2: Create the task
        GestureRecognizer = mp.tasks.vision.GestureRecognizer
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        # Create a gesture recognizer instance with the live stream mode:
        options = GestureRecognizerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_hands = 2,
            result_callback=self.save_result
        )
            
        # STEP 4: Use OpenCV’s VideoCapture to start capturing from the webcam.
        cap = cv2.VideoCapture(0)
        try:
            with GestureRecognizer.create_from_options(options) as recognizer:
                # The detector is initialized. Use it here.
                print("INITIALIZED")

                # STEP 5: Create a MediaPipe Hands instance.
                mp_drawing = mp.solutions.drawing_utils
                mp_hands = mp.solutions.hands
                hands = mp_hands.Hands(
                        static_image_mode=False,
                        max_num_hands=2,
                        min_detection_confidence=0.65,
                        min_tracking_confidence=0.65
                    )
                timestamp = 0

                # Create a loop to read the latest frame from the camera using VideoCapture#read()
                while cap.isOpened():
                    success, image = cap.read()
                    if not success:
                        print("Ignoring empty camera frame.")
                        # If loading a video, use 'break' instead of 'continue'.
                        continue

                    # flip
                    image = cv2.flip(image, 1)

                    # Convert the image to numpy.ndarray.
                    image_array = np.asarray(image)

                    # Convert the frame received from OpenCV to a MediaPipe’s Image object.
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_array)

                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    results = hands.process(image)

                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                            
                            # Run the task
                            recognizer.recognize_async(mp_image, timestamp)
                            timestamp = timestamp + 1 # should be monotonically increasing, because in LIVE_STREAM mode

                        self.put_gestures(image)

                    cv2.imshow('MediaPipe Gesture Recognition', image)
                    if cv2.waitKey(5) & 0xFF == 27:
                        break
        except Exception as e:
            print(e)
            raise

        cap.release()

    def put_gestures(self, frame):
        self.lock.acquire()
        gestures = self.current_gestures
        self.lock.release()
        y_pos = 50

        for hand_gesture_name in gestures:
            # show the prediction on the frame
            cv2.putText(frame, hand_gesture_name, (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            y_pos += 50

        """
        if len(gestures)  == 1:
            cv2.putText(frame, gestures[0], (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if len(gestures)  == 2:
            cv2.putText(frame, gestures[1], (50, y_pos + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        """

    def save_result(self, result, output_image, timestamp_ms):
        #print(f'gesture recognition result: {result}')
        self.lock.acquire() # solves potential concurrency issues
        self.current_gestures = []
        if result is not None and any(result.gestures):
            print("Recognized gestures:")
            for single_hand_gesture_data in result.gestures:
                gesture_name = single_hand_gesture_data[0].category_name
                print(gesture_name)
                self.current_gestures.append(gesture_name)
        self.lock.release()


if __name__ == '__main__':
    gesture_recognizer = GestureRecognizer()
    gesture_recognizer.main()