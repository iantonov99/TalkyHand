# To install: pip3 install tk / tkinter_webcam / opencv-python / Pillow
import tkinter as tk
from tkinter_webcam import webcam
import tkinter.scrolledtext as ScrolledText

# Create a window
window = tk.Tk()
window.title("TalkyHand")
window.geometry("1000x800")

# Webcam code
video = webcam.Box(window, width=500, height=500)
video.show_frames()

# Example chat to implement
text_widget = ScrolledText.ScrolledText(window)
text_widget.pack(fill='both', expand=True)

def send_message():
    message = entry.get()
    if message:
        text_widget.insert('end', '\nYou: ' + message)
        entry.delete(0, 'end')

# Entry widget for user input
entry = tk.Entry(window, font=("Helvetica", 14))
entry.pack(fill='x', pady=10)
entry.bind('<Return>', lambda event=None: send_message())

send_button = tk.Button(window, text="Send", command=send_message)
send_button.pack()

# Start the main loop
window.mainloop()
