import tkinter as tk
from tkinter import ttk

class CustomTkinterLabel(tk.Label):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg='white', padx=10, pady=10)

class CustomTkinterButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

class CustomTkScrollableFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.canvas = tk.Canvas(self)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor=tk.NW)

        self.frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.frame, width=event.width)

# Create the main window
root = tk.Tk()

# Create the chat frame
chat = CustomTkScrollableFrame(root)
chat.pack(fill=tk.BOTH, expand=True)

def scroll_to_bottom():
    chat.canvas.yview_moveto(1.0)

def gesturer_bt():
    label_gesturer = CustomTkinterLabel(chat.frame, wraplength=250, fg="#63359c", text="Gesture to text -> goes here")
    label_gesturer.pack()
    root.update_idletasks()  # Update the widget display
    scroll_to_bottom()

def speaker_bt():
    label_speaker = CustomTkinterLabel(chat.frame, wraplength=250, fg="#35999c", text="Speech to text is going here -> goes here")
    label_speaker.pack()
    root.update_idletasks()  # Update the widget display
    scroll_to_bottom()

button1 = CustomTkinterButton(root, text="Gesture to Text", command=gesturer_bt)
button2 = CustomTkinterButton(root, text="Speech to Text", command=speaker_bt)

button1.pack()
button2.pack()

root.mainloop()
