import tkinter as tk
import customtkinter
import cv2
from PIL import Image, ImageTk

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("TalkyHand")

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the x and y coordinates to center the window
        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2

        # Display window in the center of the screen
        self.geometry(f"1200x800+{x}+{y}")

        # configure grid layout
        self.grid_columnconfigure(0, weight=0)  # Change weight to 0 to prevent the sidebar from expanding
        self.grid_columnconfigure(1, weight=1)  # Allow the camera box to expand
        self.grid_columnconfigure(2, weight=1)  # Allow the scrollable frame to expand
        self.grid_rowconfigure(0, weight=1)

        # HEADER 
        self.header = customtkinter.CTkLabel(self, text="TalkyHand - your ASL translator Companion", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.header.place(relx=0, rely=0, relwidth=0.7, relheight=0.1)
        
        # Sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="TalkyHand", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
# ----------- CHAT  ---------------- #    -> to do: fix the resize / the right message position / the scrolling
        self.chatFrame = customtkinter.CTkFrame(self)
        self.chatFrame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.chatFrame.grid_rowconfigure(0, weight=1)  # Allow row 0 (for the chat content) to expand
        self.chatFrame.grid_columnconfigure(0, weight=1)  # Allow column 0 to expand

        self.chat = customtkinter.CTkScrollableFrame(self.chatFrame, label_text="Messages")
        self.chat.grid(row=0, sticky="nsew")

        def gesturer_bt():
            label_gesturer = customtkinter.CTkLabel(self.chat, wraplength=250, fg_color="#63359c", corner_radius=20, text="Gesture to text -> goes here")
            label_gesturer.grid(row=len(self.chat.grid_slaves()) + 1, column=1, padx=10, pady=10, sticky="nsew")
            self.chat.update()

        def speaker_bt():
            label_speaker = customtkinter.CTkLabel(self.chat, wraplength=250, fg_color="#35999c", corner_radius=20, text="Speech to text is going here -> goes here")
            label_speaker.grid(row=len(self.chat.grid_slaves()) + 1, column=2, padx=10, pady=10, sticky="nsew")
            self.chat.update()

        button1 = customtkinter.CTkButton(self, text="CTkButton", command=gesturer_bt)
        button2 = customtkinter.CTkButton(self, text="CTkButton", command=speaker_bt)
        button1.grid(row=2, column=0, padx=20, pady=10)
        button2.grid(row=3, column=0, padx=20, pady=10)

        self.entry = customtkinter.CTkEntry(self.chatFrame, placeholder_text="Text here")
        self.entry.grid(row=1, sticky="nsew")
        
# --------------------------- #
                
if __name__ == "__main__":
    app = App()
    app.mainloop()
