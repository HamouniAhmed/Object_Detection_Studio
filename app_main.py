"""
app_main.py
-----------
Entry point for Object Detection Studio.
Run this file to launch the application:

    python app_main.py
"""

import customtkinter as ctk
from app.gui import ObjectDetectionApp


if __name__ == "__main__":
    root = ctk.CTk()
    app  = ObjectDetectionApp(root)
    root.mainloop()
