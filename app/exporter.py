"""
exporter.py
-----------
Handles all file-export features:
  - Save detection results as a plain-text report (.txt)
  - Generate a formatted PDF label / report (.pdf)
"""

import datetime
from tkinter import filedialog, messagebox


def save_results_to_txt(text_content: str) -> None:
    """Prompt the user for a file path and write the results as .txt."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title="Save Detection Results"
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(_build_txt_report(text_content))
        messagebox.showinfo("Success", "Results saved successfully!")
    except Exception as exc:
        messagebox.showerror("Save Error", f"Could not save file:\n{exc}")


def generate_pdf_label(text_content: str) -> None:
    """Prompt the user for a file path and write a formatted PDF report."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas as pdfcanvas
    except ImportError:
        messagebox.showerror(
            "Missing Dependency",
            "The 'reportlab' package is required for PDF export.\n"
            "Install it with:  pip install reportlab"
        )
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Save PDF Label"
    )
    if not file_path:
        return

    try:
        c = pdfcanvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        y = height - 72

        # --- Header ---
        c.setFont("Helvetica-Bold", 18)
        c.drawString(72, y, "Object Detection Studio – Report")
        y -= 20
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawString(72, y, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
        c.setFillColorRGB(0, 0, 0)
        y -= 30

        # --- Horizontal rule ---
        c.line(72, y, width - 72, y)
        y -= 20

        # --- Body ---
        c.setFont("Helvetica", 11)
        for line in text_content.strip().split("\n"):
            if y < 72:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 72
            c.drawString(72, y, line)
            y -= 16

        c.save()
        messagebox.showinfo("Success", "PDF label generated successfully!")
    except Exception as exc:
        messagebox.showerror("PDF Error", f"Could not generate PDF:\n{exc}")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_txt_report(text_content: str) -> str:
    header = (
        "Object Detection Studio – Detection Report\n"
        f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        + "=" * 50 + "\n\n"
    )
    return header + text_content
