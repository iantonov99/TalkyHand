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
        self.geometry("1100x600")  # Fixed geometry

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the x and y coordinates to center the window
        x = (screen_width - 1100) // 2
        y = (screen_height - 600) // 2

        # Set the window's position to the center of the screen
        self.geometry(f"1100x600+{x}+{y}")

        # configure grid layout
        self.grid_columnconfigure(0, weight=0)  # Change weight to 0 to prevent the sidebar from expanding
        self.grid_columnconfigure(1, weight=1)  # Allow the camera box to expand
        self.grid_columnconfigure(2, weight=1)  # Allow the scrollable frame to expand
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="TalkyHand", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # create a canvas to display the camera feed as a square inside a larger canvas
        canvas_size = 600
        self.camera_canvas = tk.Canvas(self, width=canvas_size, height=canvas_size, bd=0, highlightthickness=0)
        self.camera_canvas.grid(row=0, column=1, padx=(20, 0), pady=20)

        # create scrollable frame
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, corner_radius=30)
        self.scrollable_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

        # Start capturing and displaying the camera feed
        self.start_camera()

    def start_camera(self):
        cap = cv2.VideoCapture(0)

        def update_camera():
            _, frame = cap.read()
            if frame is not None:
                # Avoid mirroring the camera feed
                frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

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

                # Draw rectangles on the camera feed
                self.camera_canvas.create_rectangle(50, 50, 120, 100, fill="green")  # Top left
                self.camera_canvas.create_rectangle(canvas_size // 2 - 50, 50, canvas_size // 2 + 50, 100, fill="green")  # Top center
                self.camera_canvas.create_rectangle(canvas_size - 120, 50, canvas_size - 50, 100, fill="green")  # Top right
                
            # Schedule the update function to be called after a delay (e.g., 10 ms)
            self.after(10, update_camera)

        # Start the camera update loop
        update_camera()

if __name__ == "__main__":
    app = App()
    app.mainloop()
