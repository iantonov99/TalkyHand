# to install: pip3 install tk / tkinter_webcam / opencv-python / Pillow
import tkinter as tk
from tkinter_webcam import webcam

window = tk.Tk() # Create a window
window.title("TalkyHand") # Set the title of the window
window.geometry("500x500") # Set the size of the window

# webcame code 
video = webcam.Box(window, width=500, height=500)
video.show_frames() # show the created box 

tk.mainloop() # Start the main loop

""""

# ALTERNATIVE 2

# Import required Libraries
from tkinter import *
from PIL import Image, ImageTk
import cv2

# Create an instance of TKinter Window or frame
win = Tk()

# Set the size of the window
win.geometry("700x350")

# Create a Label to capture the Video frames
label =Label(win)
label.grid(row=0, column=0)
cap= cv2.VideoCapture(0)

# Define function to show frame
def show_frames():
   # Get the latest frame and convert into Image
   cv2image= cv2.cvtColor(cap.read()[1],cv2.COLOR_BGR2RGB)
   img = Image.fromarray(cv2image)
   # Convert image to PhotoImage
   imgtk = ImageTk.PhotoImage(image = img)
   label.imgtk = imgtk
   label.configure(image=imgtk)
   # Repeat after an interval to capture continiously
   label.after(20, show_frames)

show_frames()
win.mainloop()

"""