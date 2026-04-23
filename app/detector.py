"""
detector.py
-----------
Wraps the Ultralytics YOLO model and exposes a clean inference interface.
Swap `model.pt` with any YOLOv8-compatible weights file to change the task.
"""

import cv2
from ultralytics import YOLO


# Per-class bounding-box colours (BGR)
CLASS_COLORS = [
    (255, 56,  56),   # Red
    (50,  205, 50),   # Lime Green
    (255, 191, 0),    # Amber
    (61,  145, 255),  # Sky Blue
    (255, 99,  71),   # Tomato
    (75,  0,   130),  # Indigo
    (0,   255, 255),  # Cyan
    (255, 165, 0),    # Orange
    (148, 0,   211),  # Violet
    (0,   200, 100),  # Emerald
]


class Detector:
    """Thin wrapper around a YOLO model for frame-level inference."""

    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
        self.class_colors = CLASS_COLORS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, frame):
        """Run inference on a single BGR frame and return YOLO results."""
        return self.model(frame, verbose=False)

    @property
    def names(self) -> dict:
        """Return class-id → class-name mapping from the loaded model."""
        return self.model.names

    def draw_boxes(self, frame, results) -> tuple:
        """
        Draw bounding boxes and labels onto *frame* (in-place copy).

        Returns
        -------
        annotated_frame : np.ndarray
            Frame with drawn detections.
        detections : list[dict]
            Each dict has keys: class_name, confidence, bbox (x1,y1,x2,y2).
        """
        annotated = frame.copy()
        detections = []

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls  = int(box.cls[0])
                name = self.names.get(cls, f"class_{cls}")
                color = self.class_colors[cls % len(self.class_colors)]

                # Rectangle
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

                # Label background + text
                label = f"{name}: {conf:.2f}"
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(annotated, (x1, y1 - th - 10), (x1 + tw, y1), color, -1)
                cv2.putText(annotated, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                detections.append({"class_name": name, "confidence": conf,
                                   "bbox": (x1, y1, x2, y2)})

        return annotated, detections
