import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import json
from openpyxl import Workbook

from main import process_image

mark_scheme_path = "mark_scheme.json"


def open_markscheme():
    subprocess.Popen(["python3", "gui_markscheme.py"])


def grade_single():
    path = filedialog.askopenfilename(
        filetypes=[("Images", "*.jpg *.png *.jpeg")]
    )

    if not path:
        return

    if not os.path.exists(mark_scheme_path):
        messagebox.showerror("Error", "Create mark scheme first")
        return

    with open(mark_scheme_path) as f:
        ANSWER_KEY = json.load(f)

    answers = process_image(path)

    score = sum(
        1 for i in range(min(len(answers), len(ANSWER_KEY)))
        if answers[i] == ANSWER_KEY[i]
    )

    messagebox.showinfo(
        "Result",
        f"Answers: {answers}\nScore: {score}/{len(ANSWER_KEY)}"
    )


def grade_batch():
    folder = filedialog.askdirectory()

    if not folder:
        return

    if not os.path.exists(mark_scheme_path):
        messagebox.showerror("Error", "Create mark scheme first")
        return

    with open(mark_scheme_path) as f:
        ANSWER_KEY = json.load(f)

    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    header = ["File"] + [f"Q{i+1}" for i in range(len(ANSWER_KEY))] + ["Score"]
    ws.append(header)

    for file in os.listdir(folder):
        if file.lower().endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(folder, file)

            answers = process_image(path)

            score = sum(
                1 for i in range(min(len(answers), len(ANSWER_KEY)))
                if answers[i] == ANSWER_KEY[i]
            )

            row = [file] + answers + [score]
            ws.append(row)

    wb.save("results.xlsx")
    messagebox.showinfo("Done", "Batch results saved to results.xlsx")


root = tk.Tk()
root.title("OMR Grader")
root.geometry("400x250")

tk.Label(root, text="OMR Auto Grading Tool", font=("Arial", 14)).pack(pady=10)

tk.Button(root, text="Create Mark Scheme", command=open_markscheme).pack(pady=5)

tk.Button(root, text="Grade Single Image", command=grade_single, bg="blue", fg="white").pack(pady=5)

tk.Button(root, text="Grade Folder (Batch)", command=grade_batch, bg="green", fg="white").pack(pady=5)

root.mainloop()