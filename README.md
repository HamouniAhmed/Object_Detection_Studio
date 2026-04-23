# 🔍 Object Detection Studio

> **A plug-and-play desktop application for real-time object detection — works with any YOLOv8 / Ultralytics-compatible model.**

Built with Python, [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics), and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

---

## ✨ Features

| Feature | Details |
|---|---|
| 📷 **Live Camera Detection** | Real-time inference from any webcam |
| 🖼️ **Image Detection** | Run detection on static `.jpg / .png / .bmp / .webp` files |
| 🎨 **Colour-coded Bounding Boxes** | Up to 10 per-class distinct colours |
| 📊 **Live Results Panel** | Class name + confidence score for every detection |
| 💾 **Export TXT** | Save a full detection report as a `.txt` file |
| 🖨️ **Export PDF** | Generate a formatted PDF label / report |
| 🔌 **Swap-able Model** | Drop in any YOLOv8 `.pt` file — no code changes needed |

---

## 📁 Project Structure

```
object-detection-studio/
│
├── app_main.py          ← Entry point – run this to launch the app
│
├── app/
│   ├── __init__.py
│   ├── gui.py           ← Main window (layout, controls, canvas)
│   ├── detector.py      ← YOLO model wrapper + bounding-box drawing
│   └── exporter.py      ← TXT and PDF export logic
│
├── assets/
│   └── logo.png
│
├── model.pt             ← YOLOv8n demo weights (included – ready to use)
├── requirements.txt
├── .gitignore
└── README.md
```

> **Note:** `model.pt` is the **public YOLOv8n model** trained on 80 COCO categories (Ultralytics open-source weights). You can replace it with any custom `.pt` file at any time.

---

## 🚀 Quick Start

### 1 · Clone the repository

```bash
git clone https://github.com/<your-username>/object-detection-studio.git
cd object-detection-studio
```

### 2 · Create & activate a virtual environment *(recommended)*

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3 · Install dependencies

```bash
pip install -r requirements.txt
```

### 4 · Run the app

```bash
python app_main.py
```

> `model.pt` is already included — no extra download needed. The app starts immediately.

---

## 🔌 Using Your Own Custom Model

1. Copy your YOLOv8 `.pt` file into the project root.
2. Rename it to `model.pt` (replaces the demo model).
3. Run `python app_main.py`.

The status bar will automatically display the model name and number of detected classes.

---

## 🖥️ System Requirements

| Requirement | Minimum |
|---|---|
| **Python** | 3.9+ |
| **OS** | Windows 10/11 · macOS 12+ · Ubuntu 20.04+ |
| **RAM** | 4 GB (8 GB recommended) |
| **GPU** | Optional — CUDA speeds up inference significantly |
| **Webcam** | Required only for Camera Detection mode |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `ultralytics` | YOLOv8 model loader & inference engine |
| `customtkinter` | Modern dark-themed Tkinter UI |
| `opencv-python` | Camera capture & image processing |
| `Pillow` | Image rendering on the canvas |
| `reportlab` | *(Optional)* PDF label export |

```bash
pip install -r requirements.txt
```

---

## 🗺️ How It Works

```
User Input (Camera / Image)
        │
        ▼
  ┌─────────────┐      ┌──────────────────┐
  │  app/gui.py │─────▶│ app/detector.py  │
  │   (GUI)     │      │  (YOLO Inference) │
  └─────────────┘      └──────────────────┘
        │                       │
        │   annotated frame +   │
        │   detection list      │
        ◀───────────────────────┘
        │
        ├── Canvas (live video / image)
        ├── Results panel (class + confidence)
        └── Export ──▶ app/exporter.py ──▶ .txt / .pdf
```

See [`architecture.md`](architecture.md) for the full interactive Mermaid diagrams.

---

## 📄 License

Released under the **MIT License** — free to use in personal and commercial projects.

---

## 🙌 Acknowledgements

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) — state-of-the-art real-time object detection
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — modern Tkinter theme
- [OpenCV](https://opencv.org/) — computer vision backbone

---

*Built as a reusable template for industrial and hobbyist computer vision desktop apps.*
