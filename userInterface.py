import tkinter as tk
import customtkinter
import csv
import cv2
from PIL import Image, ImageTk
import mediapipe as mp
from GestureRecognition.recognizer import GestureRecognizer

"""
from MotionRecognition.MotionRecognizer import MotionRecognizer
from MotionRecognition.utils.mediapipe_utils import mediapipe_detection
"""
from vosk import Model, KaldiRecognizer
import pyaudio
import threading

# ----------- DEFINE INTERFACE ----------- #

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Words for prediction
        self.words = []
        # Configure window
        self.title("TalkyHand")
        self.photoVoice = tk.PhotoImage(file = r"assets/voice_recognition.png")
        self.photoSign = tk.PhotoImage(file = r"assets/sign_recognition.png")

        #threat for speech recognition detection
        self.appMode = True # True - sign recognition, False - speech recognition
        self.event = threading.Event()
        self.secondary_thread = self.create_thread()
        self.secondary_thread.daemon = True  # Allow the thread to exit when the main program ends

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the x and y coordinates to center the window
        x = (screen_width - 1300) // 2
        y = (screen_height - 800) // 2

        # Display window in th
        self.geometry(f"1300x800+{x}+{y}")

        # Configure grid layout
        self.grid_columnconfigure(0, weight=0)  # Change weight to 0 to prevent the sidebar from expanding
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
        self.intro = customtkinter.CTkLabel(self.sidebar_frame, image=self.logo_photo, text="")
        self.intro.grid(row=1, column=0, sticky="nsew")
        
        # Create a label to display the logo
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, image=self.logo_photo, text="")
        self.logo_label.grid(row=1, column=0, padx=20, pady=(20, 10))
        self.logo_label.photo = self.logo_photo  # Keep a reference to the image to prevent garbage collection
        
        # Text description of TalkyHand
        self.intro = customtkinter.CTkLabel(self.sidebar_frame, wraplength=200, text="Elevate your interactions with our advanced platform. Translate sign language into text and speech, utilize autocompletion, and streamline your messages with intuitive text editing." + "\n" + "Experience the future of communication!")
        self.intro.grid(row=2, column=0, padx=20, pady=10)
        
        # Status bar providing constant feedback 
        self.status = customtkinter.CTkLabel(self.sidebar_frame)
        self.status.grid(row=4, column=0, padx=20, pady=250)
        self.status.configure(text="Status: Main page") # -> TO DO: to be updated it whenever there's a status change 
        
        # HEADER 
        self.header = customtkinter.CTkLabel(self, text="TalkyHand - your ASL translator Companion", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nw")

# ----------- CHAT ----------- # -> to do: fix the resize / the right message position / the scrolling

        self.chatFrame = customtkinter.CTkFrame(self.container)
        self.chatFrame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.chatFrame.grid_rowconfigure(0, weight=1)  # Allow row 0 (for the chat content) to expand
        self.chatFrame.grid_columnconfigure(0, weight=1)  # Allow column 0 to expand

        self.chat = customtkinter.CTkScrollableFrame(self.chatFrame, label_text="Messages", fg_color="#1d2126")
        self.chat.grid(row=0, sticky="nsew")

        def gesturer_bt():
            label_gesturer = customtkinter.CTkLabel(self.chat, wraplength=80, fg_color="#63359c", corner_radius=20)
            label_gesturer.grid(row=len(self.chat.grid_slaves()) + 1, column=1, padx=10, pady=10, sticky="w")
            self.chat.update()

        def speaker_bt():
            label_speaker = customtkinter.CTkLabel(self.chat, wraplength=80, fg_color="#35999c", corner_radius=20, text="SpeechSpeechSpeechSpeechSpeechSpeechSpeechSpeechSpeechSpeechSpeechSpeech text")
            label_speaker.grid(row=len(self.chat.grid_slaves()) + 1, column=2, padx=10, pady=10, sticky="e")
            self.chat.update()

        def changeMode():
            if self.appMode == True:
              self.event.clear()
              self.secondary_thread = self.create_thread()
              self.secondary_thread.daemon = True  # Allow the thread to exit when the main program ends
              self.secondary_thread.start()
              self.appMode = False
              changeAppModeBtn.configure(image=self.photoVoice)
            else:
              if self.event.is_set() == False:
                self.event.set()
              self.appMode = True
              changeAppModeBtn.configure(image=self.photoSign)
              
        def start_recording():
            print("starting recording...")
            speechListener.startListening()

        def stop_recording():
            print("stopping recording...")
            speechListener.stopListening()

        # Remember to edit the buttons 
        changeAppModeBtn = customtkinter.CTkButton(self.sidebar_frame, text="Change mode", image=self.photoSign, command=changeMode)
        changeAppModeBtn.grid(row=3, column=0, padx=20, pady=50)
        recordBtn = customtkinter.CTkButton(self.chatFrame, text="Record", image=self.photoVoice)
        recordBtn.grid(row=3, column=0, padx=20, pady=10)
        recordBtn.bind('<ButtonPress-1>', lambda event: start_recording())
        recordBtn.bind('<ButtonRelease-1>', lambda event: stop_recording())

        self.entry = customtkinter.CTkEntry(self.chatFrame, placeholder_text="Your speech will appear here")
        self.entry.grid(row=1, sticky="nsew")

        # create scrollable frame<
        # self.scrollable_frame = customtkinter.CTkScrollableFrame(self, corner_radius=30)
        # self.scrollable_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
        
# ----------- CAMERA ----------- #

        self.camera_canvas = tk.Canvas(self.container, width=600, height=600, bd=0, highlightthickness=0)
        self.camera_canvas.grid(row=0, column=0, padx=(20, 0), pady=20)

        # Show the autocompletion words
        self.autoC1 = customtkinter.CTkLabel(self.container, bg_color="transparent", fg_color="#eb9534", corner_radius=3, justify="center", font=("Helvetica", 20), padx=10, pady=10)
        self.autoC2 = customtkinter.CTkLabel(self.container, fg_color="#eb9534",  corner_radius=3, justify="center", font=("Helvetica", 20), padx=10, pady=10)
        self.autoC3 = customtkinter.CTkLabel(self.container, fg_color="#eb9534",  corner_radius=3, justify="center", font=("Helvetica", 20), padx=10, pady=10)

        # Show the Gesture-to-Text -> word and phrase     
        self.GTT = customtkinter.CTkLabel(self.container, corner_radius=5, fg_color="#538a50", justify="center", font=("Helvetica", 18), padx=10, pady=7)

# ----------- MODELS ----------- #

        # setup the gesture recognizer
        self.gesture_recognizer = GestureRecognizer()
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
            )

        # TODO: setup the motion recognizer
        # self.motion_recognizer = MotionRecognizer()

        self.current_message = ""

        # Start capturing and displaying the camera feed
        self.start_camera()

    def perform_gesture_recognition(self, frame_rgb):
        # Process the frame
        results = self.hands.process(frame_rgb)

        # Draw text on the frame
        if results.multi_hand_landmarks:
            # Recognize the gesture
            try:
                self.gesture_recognizer.recognize(frame_rgb, results)
            except Exception as e:
                print(f"Failed to recognize gesture: {e}")

            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame_rgb, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS, 
                    self.mp_drawing.DrawingSpec(color=(144,238,144), thickness=2, circle_radius=2), 
                )

                # Track hand position
                self.track_hand_position(hand_landmarks)

            self.GTT.configure(text=f"Recognized: {self.gesture_recognizer.get_current_gesture()}"  + "\n\n" + f"Current word: {self.gesture_recognizer.get_current_text()}_")
        else:
            self.GTT.configure(text=f"Recognized: None"  + "\n" + f"Current word: {self.gesture_recognizer.get_current_text()}_")

        self.GTT.place(x=250, y=590) 

    def track_hand_position(self, hand_landmarks):
        top_left = (0.3, 0.3)
        top_center = (0.4, 0.3)
        top_right = (0.7, 0.2)
        bottom_right = (0.7, 0.7)

        if hand_landmarks.landmark[8].x < top_left[0] and hand_landmarks.landmark[8].y < top_left[1]:
            print("TOP LEFT")
            # accept the first suggestion
            if len(self.suggestions) > 0:
                print("ADDING SUGGESTION" + self.suggestions[0][0])
                self.current_message = self.current_message + self.suggestions[0][0] + " "
                self.gesture_recognizer.reset_text()
                self.suggestions = []
        elif hand_landmarks.landmark[8].y < top_center[1] and hand_landmarks.landmark[8].x > top_center[0] and hand_landmarks.landmark[8].x < 1 - top_center[0]:
            print("TOP CENTER")
            # accept the second suggestion
            if len(self.suggestions) > 1:
                self.current_message = self.current_message + self.suggestions[1][0] + " "
                self.gesture_recognizer.reset_text()
                self.suggestions = []
        elif hand_landmarks.landmark[8].x > top_right[0] and hand_landmarks.landmark[8].y < top_right[1]:
            print("TOP RIGHT")
            # accept the third suggestion
            if len(self.suggestions) > 2:
                self.current_message = self.current_message + self.suggestions[2][0] + " "
                self.gesture_recognizer.reset_text()
                self.suggestions = []
        elif hand_landmarks.landmark[8].x > bottom_right[0] and hand_landmarks.landmark[8].y > bottom_right[1]:
            print("BOTTOM RIGHT")

    def start_camera(self):
        cap = cv2.VideoCapture(0)

        def update_camera():
            _, frame = cap.read()
            if frame is not None:
                # Avoid mirroring the camera feed
                frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

                # Perform gesture recognition
                try:
                    self.perform_gesture_recognition(frame_rgb)
                except Exception as e:
                    print(f"Failed to setup gesture recognizer: {e}")

                # if the text contains a space, then it is a word to be added to the list
                if " " in self.gesture_recognizer.get_current_text():
                    self.current_message += self.gesture_recognizer.get_current_text()
                    self.gesture_recognizer.reset_text()
                #print(self.current_message)

                # auto complete
                try:
                    self.predictCompletion(self.gesture_recognizer.get_current_text(), frame_rgb)
                except Exception as e:
                    print(f"Error in autocompletion: {e}")

                # Calculate dimensions to fit the frame within the square canvas
                canvas_size = self.camera_canvas.winfo_width()
                frame_height, frame_width, _ = frame_rgb.shape
                scale_factor = max(canvas_size / frame_width, canvas_size / frame_height)

                # Resize the frame to fill the square canvas
                frame_resized = cv2.resize(frame_rgb, (int(frame_width * scale_factor), int(frame_height * scale_factor)))

                frame_pil = Image.fromarray(frame_resized)
                frame_tk = ImageTk.PhotoImage(image=frame_pil)

                # Clear previous frame and draw the new frame on the canvas
                self.camera_canvas.delete("all")
                self.camera_canvas.create_image(canvas_size // 2, canvas_size // 2, anchor="center", image=frame_tk)
                self.camera_canvas.image = frame_tk
                
            # Schedule the update function to be called after a delay (e.g., 10 ms)
            self.after(10, update_camera)

        # Start the camera update loop
        update_camera()
    
    def predictCompletion(self, substring, frame_rgb):
        if len(substring) > 1:
            self.suggestions = [
                word
                for word in self.words
                if word[0].lower().startswith(substring.lower()) and word[0].lower() != substring.lower()
            ]
    
            self.autoC1.configure(text=self.suggestions[0][0])
            self.autoC2.configure(text=self.suggestions[1][0])
            self.autoC3.configure(text=self.suggestions[2][0])
            self.autoC1.place(x=40, y=23)
            self.autoC2.place(x=315, y=23)
            self.autoC3.place(x=600, y=23)        

    #methods for connecting the speech to text with the UI
    def writeToInput(self, text):
       self.entry.insert('end', text)
    def removeInput(self):
       self.entry.delete(0, 'end')

    def shouldStopThread(self):
      return self.event.is_set()

    def addToChat(self, textToAdd):
      label = customtkinter.CTkLabel(self.chat, wraplength=250, fg_color="#35999c", corner_radius=20, text=textToAdd)
      label.grid(row=len(self.chat.grid_slaves()) + 1, column=1, padx=10, pady=10, sticky="nsew")
      self.chat.update()

    def create_thread(self):
	    return threading.Thread(target=speech_recognition, args=(self.event,))
    

def writeToEntry(text):
   app.writeToInput(text)

def deleteInput():
   app.removeInput()

def sendToChat(text):
   app.addToChat(text)

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
                wordInSentence = text.split('with', 1)[0].strip()
                replaceString = text.split('with', 1)[1].strip()
                self.message = self.message.replace(wordInSentence, replaceString)
                print(self.message)
                deleteInput()
                writeToEntry(self.message)
        elif self.mode == 3:
            self.message = self.message.replace(text, '')
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

  def stopListening(self):
    self.mode = 0
    sendToChat(self.message)
    deleteInput()
    self.message = ""

# ----------- LOAD APP ----------- 

def speech_recognition(event):
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()
    while True:
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
        #loading file with words for prediction on finishing a word
        file = open('unigram_freq.csv')
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
