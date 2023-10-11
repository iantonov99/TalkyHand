# STEP 1: Imports
import mediapipe as mp
from mediapipe.tasks import python
import cv2
import numpy as np
import threading
import time

import socket


# source for threading: https://stackoverflow.com/questions/76320300/nameerror-name-mp-image-is-not-defined-with-mediapipe-gesture-recognition
class GestureRecognizer:
    def __init__(self, host, port):
        self.lock = threading.Lock()
        self.current_gestures = []
        self.save_text_mode = False
        self.current_letter = ""
        self.start_time = None
        self.saved_text = ""
        self.words_list = []

        self.cap = cv2.VideoCapture(0)

        self.CONFIDENCE_THRESHOLD = 0.90

        self.server_host = host
        self.server_port = port
        
        if self.server_host is not None and self.server_port is not None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.server_host, self.server_port))
            except Exception as e:
                print("Error connecting to server:", e)
                self.client_socket = None
        else:
            self.client_socket = None

        print("OK")
    
    def main(self):
        model_path = "GestureRecognizer/gesture_recognizer.task"

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
                    )
                timestamp = 0

                # Create a loop to read the latest frame from the camera using VideoCapture#read()
                while self.cap.isOpened():
                    success, image = self.cap.read()
                    h, w, c = image.shape
                    if not success:
                        print("Ignoring empty camera frame.")
                        # If loading a video, use 'break' instead of 'continue'.
                        continue

                    # Flip
                    image = cv2.flip(image, 1)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    # Convert the image to numpy.ndarray.
                    image_array = np.asarray(image)

                    # Convert the frame received from OpenCV to a MediaPipe’s Image object.
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_array)

                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    results = hands.process(image)

                    # Display saved text on the bottom left part of the frame
                    cv2.putText(image, f'Saved Text: {self.saved_text}', (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    # display the words list on the top right part of the frame, one word per line
                    y_pos = 50
                    for word in self.words_list:
                        cv2.putText(image, word, (400, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        y_pos += 50

                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                            
                            # Run the task
                            recognizer.recognize_async(mp_image, timestamp)
                            timestamp = timestamp + 1 # should be monotonically increasing, because in LIVE_STREAM mode

                            x_max = 0
                            y_max = 0
                            x_min = w
                            y_min = h
                            for lm in hand_landmarks.landmark:
                                x, y = int(lm.x * w), int(lm.y * h)
                                if x > x_max:
                                    x_max = x
                                if x < x_min:
                                    x_min = x
                                if y > y_max:
                                    y_max = y
                                if y < y_min:
                                    y_min = y
                            y_min -= 0
                            y_max += 0
                            x_min -= 0
                            x_max += 0
                            # cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                        self.put_gestures(image)

                    cv2.imshow('MediaPipe Gesture Recognition', image)

                    key = cv2.waitKey(5)
                    if key == ord('c'):  # Press space to toggle between modes
                        self.save_text_mode = not self.save_text_mode

                        if self.save_text_mode: 
                            self.saved_text = ""

                        print("Save Text Mode:", self.save_text_mode)

                    if key == ord(' '):
                        # adds the saved text to the list of words
                        self.words_list.append(self.saved_text)

                        # sends the saved text to the server
                        if self.client_socket is not None:
                            self.client_socket.sendall(self.saved_text.encode())

                        self.saved_text = ""

                    if key == ord('q'):
                        break

        except Exception as e:
            print(e)
            raise

        self.cap.release()

    def check_and_save_letter(self):
        if self.current_letter and time.time() - self.start_time >= 1:
            
            if self.current_letter == "space":
                self.saved_text += " "
            elif self.current_letter == "del":
                self.saved_text = self.saved_text[:-1]
            else:
                self.saved_text += self.current_letter

            self.current_letter = ""
            self.start_time = None

    def get_current_text(self):
        return self.saved_text

    def put_gestures(self, frame):
        self.lock.acquire()
        gestures = self.current_gestures
        self.lock.release()
        y_pos = 50

        for hand_gesture_name, hand_gesture_score in gestures:
            cv2.putText(frame, hand_gesture_name, (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f'{hand_gesture_score:.2f}', (250, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
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
        #print(f'gesture recognition result: {result}')
        self.lock.acquire() # solves potential concurrency issues
        self.current_gestures = []
        if result is not None and any(result.gestures):
            # add the gesture only if it is recognized with at least 85% confidence
            print("Recognized gestures:")
            for single_hand_gesture_data in result.gestures:
                if single_hand_gesture_data[0].score > self.CONFIDENCE_THRESHOLD:
                    gesture_name = single_hand_gesture_data[0].category_name, single_hand_gesture_data[0].score
                    print(gesture_name)
                    self.current_gestures.append(gesture_name)
                else:
                    print("Gesture not recognized with enough confidence.")
                    gesture_name = "unknown", 1 - single_hand_gesture_data[0].score
                    self.current_gestures.append(gesture_name)
        self.lock.release()
        

if __name__ == '__main__':
    MY_IP = '127.0.0.1'
    OTHER_IP = '192.168.126.52'
    PORT = 5555

    try:
        gesture_recognizer = GestureRecognizer(OTHER_IP, PORT)
        gesture_recognizer.main()
    except Exception as e:
        print(f"Failed to initialize gesture recognizer: {e}")