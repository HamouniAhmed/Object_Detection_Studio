"""
gui.py
------
Main application window for Object Detection Studio.
Handles layout construction, user interactions and wiring
together the Detector and Exporter modules.
"""

import os
import time
import threading

import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

from app.detector import Detector
from app.exporter import save_results_to_txt, generate_pdf_label


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_ROOT_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR  = os.path.join(_ROOT_DIR, "assets")
MODEL_PATH  = os.path.join(_ROOT_DIR, "model.pt")


# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
RED         = "#E8365D"
RED_HOVER   = "#C0293F"
DARK_BG     = "#1E1E2E"
PANEL_BG    = "#2A2A3C"
CARD_BG     = "#313145"
ACCENT      = "#7C3AED"
ACCENT_HVR  = "#6D28D9"
WHITE       = "#FFFFFF"
BLACK       = "#000000"
TEXT_DIM    = "#A0A0B8"


# ---------------------------------------------------------------------------
# Main application window
# ---------------------------------------------------------------------------
class ObjectDetectionApp:
    

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Object Detection Studio")
        self.root.geometry("1280x820")
        self.root.minsize(900, 600)

        ctk.set_appearance_mode("Dark")
        self.root.configure(fg_color=DARK_BG)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_controls()
        self._build_main_area()
        self._build_status_bar()
        self._init_state()
        self._load_model()

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    # ------------------------------------------------------------------
    # Layout builders
    # ------------------------------------------------------------------

    def _build_header(self):
        header = ctk.CTkFrame(self.root, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 8), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        try:
            logo_img = ctk.CTkImage(Image.open(logo_path), size=(160, 56))
            ctk.CTkLabel(header, image=logo_img, text="").grid(
                row=0, column=0, padx=(0, 16), sticky="w"
            )
        except FileNotFoundError:
            ctk.CTkLabel(
                header, text="🔍 ODS",
                font=ctk.CTkFont(size=22, weight="bold"), text_color=ACCENT
            ).grid(row=0, column=0, padx=(0, 16), sticky="w")

        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            title_col, text="Object Detection Studio",
            font=ctk.CTkFont(size=26, weight="bold"), text_color=WHITE
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_col, text="Camera & Image modes",
            font=ctk.CTkFont(size=12), text_color=TEXT_DIM
        ).pack(anchor="w")

    def _build_controls(self):
        bar = ctk.CTkFrame(self.root, fg_color=PANEL_BG, corner_radius=12)
        bar.grid(row=1, column=0, padx=24, pady=8, sticky="ew")

        self.detection_mode = ctk.CTkComboBox(
            bar, values=["Camera Detection", "Image Detection"],
            command=self.set_detection_mode, state="readonly",
            button_color=RED, button_hover_color=RED_HOVER,
            dropdown_fg_color=CARD_BG, width=180
        )
        self.detection_mode.set("Camera Detection")
        self.detection_mode.pack(side="left", padx=12, pady=10)

        self.browse_button = ctk.CTkButton(
            bar, text="📂  Browse Image", command=self.browse_image,
            state="disabled", fg_color=PANEL_BG, hover_color=CARD_BG,
            border_width=1, border_color=RED, text_color=RED, width=140
        )
        self.browse_button.pack(side="left", padx=6, pady=10)

        self.start_button = ctk.CTkButton(
            bar, text="▶  Start", command=self.start_detection,
            fg_color=RED, hover_color=RED_HOVER, width=120
        )
        self.start_button.pack(side="left", padx=6, pady=10)

        self.stop_button = ctk.CTkButton(
            bar, text="⏹  Stop", command=self.stop_detection,
            state="disabled", fg_color=ACCENT, hover_color=ACCENT_HVR, width=120
        )
        self.stop_button.pack(side="left", padx=6, pady=10)

        # Right-side actions
        self.print_button = ctk.CTkButton(
            bar, text="🖨  PDF Label", command=self._on_print,
            fg_color=PANEL_BG, hover_color=CARD_BG,
            border_width=1, border_color=ACCENT, text_color=ACCENT, width=130
        )
        self.print_button.pack(side="right", padx=12, pady=10)

        self.save_button = ctk.CTkButton(
            bar, text="💾  Save TXT", command=self._on_save,
            fg_color=PANEL_BG, hover_color=CARD_BG,
            border_width=1, border_color=WHITE, text_color=WHITE, width=130
        )
        self.save_button.pack(side="right", padx=6, pady=10)

    def _build_main_area(self):
        main = ctk.CTkFrame(self.root, fg_color="transparent")
        main.grid(row=2, column=0, padx=24, pady=8, sticky="nsew")
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # Video / image canvas
        canvas_frame = ctk.CTkFrame(main, fg_color=BLACK, corner_radius=12)
        canvas_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = ctk.CTkCanvas(canvas_frame, background=BLACK, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # Sidebar results panel
        sidebar = ctk.CTkFrame(main, fg_color=PANEL_BG, corner_radius=12)
        sidebar.grid(row=0, column=1, sticky="nsew")
        sidebar.grid_rowconfigure(2, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sidebar, text="Detection Results",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=WHITE
        ).grid(row=0, column=0, padx=14, pady=(14, 4), sticky="w")

        self.detection_count_label = ctk.CTkLabel(
            sidebar, text="Objects found: –",
            font=ctk.CTkFont(size=11), text_color=TEXT_DIM
        )
        self.detection_count_label.grid(row=1, column=0, padx=14, pady=(0, 8), sticky="w")

        self.result_text = ctk.CTkTextbox(
            sidebar,
            font=ctk.CTkFont(family="Consolas", size=12),
            border_width=0, fg_color=CARD_BG, corner_radius=8,
            text_color=WHITE
        )
        self.result_text.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def _build_status_bar(self):
        bar = ctk.CTkFrame(self.root, fg_color=PANEL_BG, corner_radius=8, height=30)
        bar.grid(row=3, column=0, padx=24, pady=(4, 12), sticky="ew")

        self.status_label = ctk.CTkLabel(
            bar, text="●  Idle", anchor="w",
            font=ctk.CTkFont(size=12), text_color=TEXT_DIM
        )
        self.status_label.pack(side="left", padx=14, pady=4)

        self.model_label = ctk.CTkLabel(
            bar, text=f"Model: {os.path.basename(MODEL_PATH)}",
            anchor="e", font=ctk.CTkFont(size=11), text_color=TEXT_DIM
        )
        self.model_label.pack(side="right", padx=14, pady=4)

    # ------------------------------------------------------------------
    # State initialisation & model loading
    # ------------------------------------------------------------------

    def _init_state(self):
        self.cap          = None
        self.running      = False
        self.current_mode = "Camera Detection"
        self.image_path   = ""
        self.detector     = None

    def _load_model(self):
        if not os.path.exists(MODEL_PATH):
            messagebox.showerror(
                "Model Not Found",
                f"'{os.path.basename(MODEL_PATH)}' was not found in the project root.\n\n"
                "Run the following command to download a demo model:\n"
                "    python download_model.py\n\n"
                "Or place your own YOLOv8 .pt file here and rename it 'model.pt'."
            )
            self.root.after(100, self.root.destroy)
            return

        self.detector = Detector(MODEL_PATH)
        self.model_label.configure(
            text=f"Model: {os.path.basename(MODEL_PATH)}  ·  {len(self.detector.names)} classes"
        )

    # ------------------------------------------------------------------
    # Mode & navigation
    # ------------------------------------------------------------------

    def set_detection_mode(self, mode: str):
        self.current_mode = mode
        if self.running:
            self.stop_detection()
        if mode == "Image Detection":
            self.browse_button.configure(state="normal")
        else:
            self.browse_button.configure(state="disabled")
            self.image_path = ""
            self.canvas.delete("all")

    def browse_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if path:
            self.image_path = path
            self._set_status(f"Loaded: {os.path.basename(path)}", idle=True)
            frame = cv2.imread(path)
            self._display_frame(frame)

    # ------------------------------------------------------------------
    # Detection control
    # ------------------------------------------------------------------

    def start_detection(self):
        if self.running or self.detector is None:
            return

        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.running = True

        if self.current_mode == "Camera Detection":
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror(
                    "Camera Error",
                    "Could not open camera. Make sure it is connected\n"
                    "and not used by another application."
                )
                self.stop_detection()
                return
            self._set_status("● Running  –  Camera Detection")
            threading.Thread(target=self._camera_loop, daemon=True).start()

        elif self.current_mode == "Image Detection":
            if not self.image_path or not os.path.exists(self.image_path):
                messagebox.showerror("No Image", "Please select an image file first.")
                self.stop_detection()
                return
            self._set_status("⏳ Processing image…")
            threading.Thread(target=self._image_once, daemon=True).start()

    def stop_detection(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self._set_status("●  Idle", idle=True)

    # ------------------------------------------------------------------
    # Inference threads
    # ------------------------------------------------------------------

    def _camera_loop(self):
        while self.running:
            if self.cap is None:
                break
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.5)
                continue
            results = self.detector.detect(frame)
            self.root.after(0, self._render_results, frame, results)
            time.sleep(0.01)

    def _image_once(self):
        frame   = cv2.imread(self.image_path)
        results = self.detector.detect(frame)
        self.root.after(0, self._render_results, frame, results)
        self.root.after(200, self.stop_detection)

    # ------------------------------------------------------------------
    # Render helpers
    # ------------------------------------------------------------------

    def _render_results(self, frame, results):
        if not self.running and self.current_mode != "Image Detection":
            return

        annotated, detections = self.detector.draw_boxes(frame, results)

        self.result_text.delete("1.0", "end")
        self.detection_count_label.configure(
            text=f"Objects found: {len(detections)}"
        )

        if detections:
            for d in detections:
                self.result_text.insert(
                    "end",
                    f"▸ {d['class_name']}\n"
                    f"  Confidence: {d['confidence']:.2%}\n\n"
                )
        else:
            self.result_text.insert("end", "No objects detected.")

        self._display_frame(annotated)

    def _display_frame(self, frame):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return

        h, w = frame.shape[:2]
        ratio = w / h

        if w > cw or h > ch:
            if (cw / ratio) <= ch:
                new_w, new_h = cw, int(cw / ratio)
            else:
                new_h, new_w = ch, int(ch * ratio)
            frame = cv2.resize(frame, (new_w, new_h))

        from PIL import Image as PILImage
        img   = PILImage.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)

        x = (cw - img.width)  // 2
        y = (ch - img.height) // 2

        self.canvas.delete("all")
        self.canvas.create_image(x, y, anchor="nw", image=imgtk)
        self.canvas.imgtk = imgtk  # prevent GC

    # ------------------------------------------------------------------
    # Export callbacks
    # ------------------------------------------------------------------

    def _on_save(self):
        save_results_to_txt(self.result_text.get("1.0", "end"))

    def _on_print(self):
        generate_pdf_label(self.result_text.get("1.0", "end"))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _set_status(self, msg: str, idle: bool = False):
        color = TEXT_DIM if idle else WHITE
        self.status_label.configure(text=msg, text_color=color)

    def close_app(self):
        if self.running:
            self.stop_detection()
            time.sleep(0.1)
        self.root.destroy()
