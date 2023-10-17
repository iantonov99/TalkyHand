import tkinter as tk
import customtkinter
import csv
import cv2
from PIL import Image, ImageTk
import mediapipe as mp
import os
from dotenv import load_dotenv

from GestureRecognition.recognizer import GestureRecognizer
from MotionRecognition.MotionRecognizer import MotionRecognizer

from vosk import Model, KaldiRecognizer
import pyaudio
import threading

from chatSender import ChatSender
import socket

import gtts
from playsound import playsound

load_dotenv()

# ----------- DEFINE INTERFACE ----------- #

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("Dark")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("green")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        def changeMode():
            if self.appMode == True:
                self.event.clear()
                self.speech_thread = self.create_thread()
                # Allow the thread to exit when the main program ends
                self.speech_thread.daemon = True
                self.speech_thread.start()
                self.appMode = False
                changeAppModeBtn.configure(image=self.photoVoice)
                self.recordBtn.configure(image=self.recVoice)
                self.status.configure(text="Status: Recording voice mode")
            else:
                if self.event.is_set() == False:
                    self.event.set()
                self.appMode = True
                changeAppModeBtn.configure(image=self.photoSign)
                self.status.configure(text="Status: Gesture recognition mode")

        def start_recording():
            print("starting recording...")
            speechListener.startListening()
            self.status.configure(text="Status: Is recording")

        def stop_recording():
            print("stopping recording...")
            speechListener.stopListening()
            self.status.configure(text="Status: Stop recording")

        def recordBtnAction(self):
            if self.appMode == True:
                self.is_recording = not self.is_recording
                self.motion_recognizer.start_motion()
                self.gesture_recognizer.flip_save_text_mode()
                if self.is_recording == True:
                    changeAppModeBtn.configure(state=tk.DISABLED)
                else:
                    changeAppModeBtn.configure(state=tk.NORMAL)
                    self.gesture_recognizer.reset_text()
                print("Tracking recognition")
                self.status.configure(text="Status: Tracking recognition")
            else:
                if speechListener.getSpeechMode() == 0:
                    start_recording()
                    changeAppModeBtn.configure(state=tk.DISABLED)
                else:
                    stop_recording()
                    changeAppModeBtn.configure(state=tk.NORMAL)

            self.actionButtonActive = not self.actionButtonActive

            if self.actionButtonActive:
                self.recordBtn.configure(fg_color="#729c59", hover_color="#5f8c50")
            else:
                self.recordBtn.configure(fg_color="#9c6359", hover_color="#8c5a50")

        self.hostname = str(os.getenv("HOSTNAME"))
        self.port = int(os.getenv("PORT"))

        # create a chatsender as a separate thread
        self.sender = ChatSender(self.hostname, self.port)
        self.sender_thread = threading.Thread(target=self.sender.setup_client)
        self.sender_thread.daemon = True
        self.sender_thread.start()

        # CHAT RECEIVER
        self.server_host = "0.0.0.0"
        self.server_port = 5555
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(1)  # Maximum 1 connection at a time
        self.client_socket, self.client_address = self.server_socket.accept()

        print("ACCEPTED CONNECTION")

        receiver_thread = threading.Thread(target=self.receive_messages)
        receiver_thread.daemon = True
        receiver_thread.start()

        # ----------- MODELS ----------- #

        self.cap = cv2.VideoCapture(0)

        # setup the gesture recognizer
        self.gesture_recognizer = GestureRecognizer()
        self.mp_drawing = mp.solutions.drawing_utils  # type: ignore
        self.mp_hands = mp.solutions.hands  # type: ignore
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
        )

        # setup the motion recognizer
        self.motion_recognizer = MotionRecognizer(self.cap)
        self.is_recording = False

        self.current_message = ""
        self.actionButtonActive = False

        # Words for prediction
        self.words = []
        self.suggestions = []
        # Configure window
        self.title("TalkyHand")
        self.photoVoice = tk.PhotoImage(file=r"assets/voice_recognition.png")
        self.photoSign = tk.PhotoImage(file=r"assets/sign_recognition.png")
        self.sentLogo = tk.PhotoImage(file=r"assets/sentLogo.png")
        self.recVoice = tk.PhotoImage(file=r"assets/recording.png")
        self.recHand = tk.PhotoImage(file=r"assets/gestures.png")
        # threat for speech recognition detection
        self.appMode = True  # True - sign recognition, False - speech recognition
        self.event = threading.Event()
        self.speech_thread = self.create_thread()
        # Allow the thread to exit when the main program ends
        self.speech_thread.daemon = True

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the x and y coordinates to center the window
        x = (screen_width - 1350) // 2
        y = (screen_height - 800) // 2

        # Display window in th
        self.geometry(f"1350x800+{x}+{y}")

        # Configure grid layout
        # Change weight to 0 to prevent the sidebar from expanding
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)  # Grid for the main container
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # ----------- CONTAINTER ----------- # -> TO CHECK: whether to leave it or just structure more the grid withoud using a container

        self.container = customtkinter.CTkFrame(self)
        self.container.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)

        # SIDEBAR - navigation
        self.sidebar_frame = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")

        # Image logo
        self.logo_image = Image.open("assets/TalkyHand.png")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.intro = customtkinter.CTkLabel(
            self.sidebar_frame, image=self.logo_photo, text=""
        )
        self.intro.grid(row=1, column=0, sticky="nsew")

        # Create a label to display the logo
        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame, image=self.logo_photo, text=""
        )
        self.logo_label.grid(row=1, column=0, padx=20, pady=(20, 10))
        self.logo_label.photo = (
            self.logo_photo
        )  # Keep a reference to the image to prevent garbage collection

        # Text description of TalkyHand
        self.intro = customtkinter.CTkLabel(
            self.sidebar_frame,
            wraplength=200,
            text="Elevate your interactions with our advanced platform. Translate sign language into text and speech, utilize autocompletion, and streamline your messages with intuitive text editing."
            + "\n\n"
            + "Experience the future of communication!",
        )
        self.intro.grid(row=2, column=0, padx=20, pady=10)

        # Status bar providing constant feedback
        self.status = customtkinter.CTkLabel(self.sidebar_frame)
        self.status.grid(row=4, column=0, padx=20, pady=250)
        self.status.configure(
            text="Status: Main page"
        )  # -> to update whenever there's a status change

        # HEADER
        self.header = customtkinter.CTkLabel(
            self,
            text="TalkyHand - your ASL translator Companion",
            font=customtkinter.CTkFont(size=24, weight="bold"),
        )
        self.header.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nw")

        # ----------- CHAT ----------- # -> to do: fix the resize / the right message position / the scrolling

        self.chatFrame = customtkinter.CTkFrame(self.container)
        self.chatFrame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Allow row 0 (for the chat content) to expand
        self.chatFrame.grid_rowconfigure(0, weight=1)
        self.chatFrame.grid_columnconfigure(0, weight=1)  # Allow column 0 to expand
        self.chatFrame.grid_columnconfigure(1, weight=1)

        self.chat = customtkinter.CTkScrollableFrame(
            self.chatFrame, label_text="Messages", fg_color="#1d2126"
        )
        self.chat.grid(row=0, sticky="nsew")

        # Remember to edit the buttons
        changeAppModeBtn = customtkinter.CTkButton(
            self.sidebar_frame,
            text="Change mode",
            image=self.photoSign,
            command=changeMode,
        )
        changeAppModeBtn.grid(row=3, column=0, padx=20, pady=30)

        self.chatButtonContainer = customtkinter.CTkFrame(self.chatFrame)
        self.chatButtonContainer.grid(row=1, padx=20, pady=10)
        self.chatButtonContainer.grid_rowconfigure(0, weight=1)
        self.chatButtonContainer.grid_rowconfigure(1, weight=1)
        self.chatButtonContainer.grid_columnconfigure(
            0, weight=1
        )  # Allow column 0 to expand
        self.chatButtonContainer.grid_columnconfigure(1, weight=1)

        self.entry = customtkinter.CTkEntry(
            self.chatButtonContainer, placeholder_text="Your output will appear here"
        )
        self.entry.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.recordBtn = customtkinter.CTkButton(
            self.chatButtonContainer,
            image=self.recHand,
            text="Record",
            fg_color="#9c6359",
            hover_color="#8c5a50",
            command=lambda: recordBtnAction(self),
        )
        self.recordBtn.grid(row=1, column=0, padx=20, pady=10)

        self.sendBtn = customtkinter.CTkButton(
            self.chatButtonContainer,
            image=self.sentLogo,
            text="Send",
            fg_color="#59939c",
            command=lambda: self.send_message(self.entry.get()),
        )
        self.sendBtn.grid(row=1, column=1, padx=20, pady=10)

        # create scrollable frame
        # self.scrollable_frame = customtkinter.CTkScrollableFrame(self, corner_radius=30)
        # self.scrollable_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

        # ----------- CAMERA ----------- #

        self.cap = cv2.VideoCapture(0)

        self.camera_canvas = tk.Canvas(
            self.container,
            width=600,
            height=600,
            bd=0,
            highlightthickness=0,
            bg="#2b2b2b",
        )
        self.camera_canvas.grid(row=0, column=0, padx=(20, 0), pady=20)

        # Show the Gesture-to-Text -> word and phrase
        self.GTT = customtkinter.CTkLabel(
            self.container,
            corner_radius=5,
            fg_color="#538a50",
            justify="center",
            font=("Helvetica", 18),
            padx=10,
            pady=7,
        )

        self.receive_message("This is where you will see your friend's messages!")
        self.addToChat("This is where you will see your messages!")

        # Start capturing and displaying the camera feed
        self.start_camera()

    def receive_messages(self):
        print("LISTENING:")
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                received_text = data.decode()
                print("Received:", received_text)
                self.receive_message(received_text)

            except ConnectionResetError:
                print("Connection closed by the other side.")
                break

    def send_message(self, message):
        if message:
            print("SENDING:", message)
            self.addToChat(message)
            deleteInput()
            if self.sender != None:
                self.sender.send_message(message)

    def draw_landmarks(self, results, frame_rgb):
        # Draw text on the frame
        # cv2.putText(frame_rgb, f'Current word: {self.gesture_recognizer.get_current_text()}_', (80, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame_rgb,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(
                        color=(144, 238, 144), thickness=2, circle_radius=2
                    ),
                )

                # Track hand position
                self.track_hand_position(hand_landmarks)

            self.GTT.configure(
                text=f"Recognized: {self.gesture_recognizer.get_current_gesture()}"
                + "\n\n"
                + f"Current word: {self.gesture_recognizer.get_current_text()}_"
            )
        else:
            self.GTT.configure(
                text=f"Recognized: None"
                + "\n"
                + f"Current word: {self.gesture_recognizer.get_current_text()}_"
            )

        self.GTT.place(x=250, y=590)

    def track_hand_position(self, hand_landmarks):
        top_left = (0.3, 0.3)
        top_center = (0.4, 0.3)
        top_right = (0.7, 0.2)
        bottom_right = (0.85, 0.85)

        if (
            hand_landmarks.landmark[8].x < top_left[0]
            and hand_landmarks.landmark[8].y < top_left[1]
            and self.gesture_recognizer.get_save_text_mode()
        ):
            print("TOP LEFT")
            # accept the first suggestion
            if len(self.suggestions) > 1:
                print("ADDING SUGGESTION: " + self.suggestions[1][0])
                self.current_message = (
                    self.current_message + self.suggestions[1][0] + " "
                )
                self.writeToInput(self.suggestions[1][0] + " ")
                self.gesture_recognizer.reset_text()
                self.suggestions = []
        elif (
            hand_landmarks.landmark[8].y < top_center[1]
            and hand_landmarks.landmark[8].x > top_center[0]
            and hand_landmarks.landmark[8].x < 1 - top_center[0]
            and self.gesture_recognizer.get_save_text_mode()
        ):
            print("TOP CENTER")
            # accept the second suggestion
            if len(self.suggestions) > 0:
                self.current_message = (
                    self.current_message + self.suggestions[0][0] + " "
                )
                self.writeToInput(self.suggestions[0][0] + " ")
                self.gesture_recognizer.reset_text()
                self.suggestions = []
        elif (
            hand_landmarks.landmark[8].x > top_right[0]
            and hand_landmarks.landmark[8].y < top_right[1]
            and self.gesture_recognizer.get_save_text_mode()
        ):
            print("TOP RIGHT")
            # accept the third suggestion
            if len(self.suggestions) > 2:
                self.current_message = (
                    self.current_message + self.suggestions[2][0] + " "
                )
                self.writeToInput(self.suggestions[2][0] + " ")
                self.gesture_recognizer.reset_text()
                self.suggestions = []
        elif (
            hand_landmarks.landmark[8].x > bottom_right[0]
            and hand_landmarks.landmark[8].y > bottom_right[1]
            and self.gesture_recognizer.get_save_text_mode()
        ):
            print("BOTTOM RIGHT")
            if self.entry.get():
                self.send_message(self.entry.get())

    def start_camera(self):
        def update_camera():
            _, frame = self.cap.read()
            if frame is not None:
                # Avoid mirroring the camera feed
                frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
                results = self.hands.process(frame_rgb)

                # Perform gesture recognition
                try:
                    if self.gesture_recognizer.get_save_text_mode():
                        self.gesture_recognizer.recognize(frame_rgb)

                        # auto complete
                        try:
                            self.predictCompletion(
                                self.gesture_recognizer.get_current_text(), frame_rgb
                            )
                        except Exception as e:
                            print(f"Error in autocompletion: {e}")
                except Exception as e:
                    print(f"Failed to setup gesture recognizer: {e}")

                # if the text contains a space, then it is a word to be added to the list
                if " " in self.gesture_recognizer.get_current_text():
                    self.current_message += self.gesture_recognizer.get_current_text()
                    self.writeToInput(self.gesture_recognizer.get_current_text() + " ")
                    self.gesture_recognizer.reset_text()

                # Perform motion recognition
                try:
                    if self.motion_recognizer.is_recording():
                        flipped_frame = cv2.flip(frame_rgb, 1)

                        motion_detected = self.motion_recognizer.analyze(flipped_frame)

                        if motion_detected is not None:
                            print(motion_detected)
                            if motion_detected != "Unknown sign":
                                self.current_message += motion_detected
                                self.writeToInput(motion_detected + " ")
                            else:
                                print("Unknown sign detected")
                                self.status.configure(
                                    text="Status: Unknown sign detected"
                                )

                except Exception as e:
                    print(f"Failed analysys with motion recognizer: {e}")

                self.draw_landmarks(results, frame_rgb)

                # draw and fill a small orange rectangle on the bottom right corner of the camera canvas (with written "Send") (it should be inside the canvas)
                cv2.rectangle(
                    frame_rgb,
                    (frame_rgb.shape[1] - 100, frame_rgb.shape[0] - 50),
                    (frame_rgb.shape[1], frame_rgb.shape[0]),
                    (255, 165, 0),
                    -1,
                )
                # write "Send" inside the rectangle
                cv2.putText(
                    frame_rgb,
                    "Send",
                    (frame_rgb.shape[1] - 100, frame_rgb.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )

                # Calculate dimensions to fit the frame within the square canvas
                canvas_size = self.camera_canvas.winfo_width()
                frame_height, frame_width, _ = frame_rgb.shape
                scale_factor = max(
                    canvas_size / frame_width, canvas_size / frame_height
                )

                # Resize the frame to fill the square canvas
                frame_resized = frame_rgb

                frame_pil = Image.fromarray(frame_resized)
                frame_tk = ImageTk.PhotoImage(image=frame_pil)

                # Clear previous frame and draw the new frame on the canvas
                self.camera_canvas.delete("all")
                self.camera_canvas.create_image(
                    canvas_size // 2, canvas_size // 2, anchor="center", image=frame_tk
                )
                self.camera_canvas.image = frame_tk

            # Schedule the update function to be called after a delay (e.g., 10 ms)
            self.after(10, update_camera)

        # Start the camera update loop
        update_camera()

    def predictCompletion(self, substring, frame_rgb):
        self.suggestions = []

        if len(substring) > 1:
            self.suggestions = [
                word
                for word in self.words
                if word[0].lower().startswith(substring.lower())
                and word[0].lower() != substring.lower()
            ]

            if len(self.suggestions) > 0:
                # first suggestion to the middle, second to the left and third one to the right
                # draw and fill a small orange rectangle on the top left corner of the camera canvas of the size of the first suggestion
                frame_x = frame_rgb.shape[1]

                # draw and fill a small orange rectangle on the top center corner of the camera canvas of the size of the second suggestion
                cv2.rectangle(
                    frame_rgb,
                    (frame_x // 2 - len(self.suggestions[0][0]) * 20 // 2, 23),
                    (
                        frame_x // 2 + (len(self.suggestions[0][0]) - 1) * 20 // 2,
                        23 + 30,
                    ),
                    (255, 165, 0),
                    -1,
                )
                # write the second suggestion inside the second rectangle
                cv2.putText(
                    frame_rgb,
                    self.suggestions[0][0],
                    (frame_x // 2 - len(self.suggestions[0][0]) * 20 // 2, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )

                if len(self.suggestions) > 1:
                    cv2.rectangle(
                        frame_rgb,
                        (40, 23),
                        (40 + len(self.suggestions[1][0]) * 20 - 20, 23 + 30),
                        (255, 165, 0),
                        -1,
                    )
                    # write the first suggestion inside the first rectangle
                    cv2.putText(
                        frame_rgb,
                        self.suggestions[1][0],
                        (40, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        2,
                    )

                    if len(self.suggestions) > 2:
                        # draw and fill a small orange rectangle on the top right corner of the camera canvas of the size of the third suggestion
                        cv2.rectangle(
                            frame_rgb,
                            (frame_x - 40 - len(self.suggestions[2][0]) * 20, 23),
                            (frame_x - 40, 23 + 30),
                            (255, 165, 0),
                            -1,
                        )

                        # write the third suggestion inside the third rectangle
                        cv2.putText(
                            frame_rgb,
                            self.suggestions[2][0],
                            (frame_x - 40 - len(self.suggestions[2][0]) * 20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 255, 255),
                            2,
                        )

    # methods for connecting the speech to text with the UI
    def writeToInput(self, text):
        self.entry.insert("end", text)

    def removeInput(self):
        self.entry.delete(0, "end")

    def shouldStopThread(self):
        return self.event.is_set()

    def addToChat(self, textToAdd):
        label = customtkinter.CTkLabel(
            self.chat,
            wraplength=148,
            fg_color="#76acdb",
            corner_radius=20,
            text=textToAdd,
        )
        label.grid(
            row=len(self.chat.grid_slaves()) + 1,
            column=1,
            padx=10,
            pady=10,
            sticky="e",
        )
        label.bind("<Button-1>", lambda e, text=textToAdd: labelClicked(text=textToAdd))
        self.chat.update()

    def receive_message(self, textReceived):
        label = customtkinter.CTkLabel(
            self.chat,
            wraplength=148,
            fg_color="#7a76db",
            corner_radius=20,
            text=textReceived,
        )
        label.grid(
            row=len(self.chat.grid_slaves()) + 1,
            column=0,
            padx=10,
            pady=10,
            sticky="w",
        )
        label.bind(
            "<Button-1>", lambda e, text=textReceived: labelClicked(text=textReceived)
        )
        self.chat.update()

    def create_thread(self):
        return threading.Thread(target=speech_recognition, args=(self.event,))


def writeToEntry(text):
    app.writeToInput(text)


def deleteInput():
    app.removeInput()


def sendToChat(text):
    app.addToChat(text)


def labelClicked(text):
    try:
        # Specify the text, language, and gender
        language = "en"  # Language code for English
        accent = "us"

        # Create the gTTS object with speed control and male voice
        tts = gtts.gTTS(text, lang=language, slow=False, tld=accent)

        # Save the TTS output to a file
        tts.save("Readable.mp3")

        # Play the generated audio on a separate thread
        audio_thread = threading.Thread(target=playAudio)
        audio_thread.Daemon = True
        audio_thread.start()
    except Exception as e:
        print(f"Failed to play audio: {e}")


def playAudio():
    playsound("Readable.mp3")

    # Delete the file
    os.remove("Readable.mp3")


class SpeechListener:
    def __init__(self):
        self.stop_listening = None
        self.shouldWriteToChat = False
        self.message = ""
        self.mode = 0

    def writeToInput(self, text):
        if self.mode != 0:
            if self.mode == 1:
                if self.message != "":
                    self.message = self.message + " "
                    writeToEntry(" ")
                self.message = self.message + text
                writeToEntry(text)
            elif self.mode == 2:
                if "with" in text:
                    wordInSentence = text.split("with", 1)[0].strip()
                    replaceString = text.split("with", 1)[1].strip()
                    self.message = self.message.replace(wordInSentence, replaceString)
                    print(self.message)
                    deleteInput()
                    writeToEntry(self.message)
            elif self.mode == 3:
                self.message = self.message.replace(text, "")
                print(self.message)
                deleteInput()
                writeToEntry(self.message)

    def commands(self, text):
        if text == "continue":
            self.mode = 1
        elif text == "replace":
            self.mode = 2
        elif text == "remove":
            self.mode = 3
        elif text == "again":
            deleteInput()
            self.message = ""
        else:
            print("unknown command.")

    def startListening(self):
        self.mode = 1
        self.message = ""

    def stopListening(self):
        self.mode = 0
        app.send_message(self.message)
        self.message = ""

    def getSpeechMode(self):
        return self.mode


# ----------- LOAD APP -----------


def speech_recognition(event):
    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8192,
    )

    while True:
        stream.start_stream()

        while speechListener.getSpeechMode() != 0:
            if app.shouldStopThread() == True:
                break

            data = stream.read(4096)

            if recognizer.AcceptWaveform(data):
                text = recognizer.Result()
                text = text[14:-3]
                print(text)

                if text in ["continue", "replace", "remove", "again"]:
                    speechListener.commands(text)
                else:
                    speechListener.writeToInput(text)

        stream.stop_stream()


# Create a separate thread for the secondary loop
if __name__ == "__main__":
    try:
        app = App()
        # loading file with words for prediction on finishing a word
        file = open("unigram_freq.csv")
        type(file)
        csvreader = csv.reader(file)
        for row in csvreader:
            app.words.append(row)

        speechListener = SpeechListener()
        model = Model("vosk-model-small-en-us-0.15")

        recognizer = KaldiRecognizer(model, 16000)

        mic = pyaudio.PyAudio()

        app.mainloop()
    except Exception as e:
        print(f"Failed to run app: {e}")
