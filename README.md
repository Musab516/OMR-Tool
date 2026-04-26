Here is the updated `README.md` tailored exactly to the Python code we just built. It reflects the new CSV export system, the single-file Tkinter architecture, the new ERP extraction feature, and adds Emad Yar Khan to the team.

```markdown
# OMR Evaluation System

A Python-based Optical Mark Recognition (OMR) application that automatically detects, extracts, and grades MCQ answer sheets and Student IDs (ERP) using computer vision.

---

## 🚀 Features

* **Smart Document Alignment:** Uses OpenCV contour detection and perspective transformation to automatically warp and flatten photographed or scanned sheets.
* **ERP / Student ID Extraction:** Accurately reads 5-digit student roll numbers from complex, split-grid bubble layouts.
* **Accurate Grading:** Detects answers for up to 41 questions (Options A, B, C, D) using pixel darkness thresholds.
* **Interactive GUI:** Built-in Tkinter dashboard for easy operation without using the command line.
* **Markscheme Editor:** Scrollable, interactive UI to set and save the correct answer key.
* **Batch Processing:** Automatically process an entire folder of scanned OMR sheets in seconds.
* **CSV Exports:** Automatically generates detailed `student_result.csv` for single scans and a master `batch_results.csv` for folder processing.

---

## 🧠 How It Works

1. **Image Preprocessing:** Converts the image to grayscale, applies Gaussian blur, and uses adaptive thresholding.
2. **Perspective Warping:** Finds the 4 largest corners of the OMR boundary and warps the image into a perfect 800x1000 top-down view.
3. **ERP Extraction:** Scans a calibrated 10x5 coordinate grid (with split-gap logic) to extract the student's 5-digit ID.
4. **Answer Extraction:** Scans the Left (Q1-21) and Right (Q22-41) columns, measuring the pixel density (`cv2.countNonZero`) of each bubble to find the darkest option.
5. **Evaluation:** Compares the detected answers against the saved `markscheme.csv` and calculates Correct, Incorrect, and Blank totals.

---

## 📁 Project Structure

```text
OMR-Evaluation-System/
│
├── main.py              # Main application script (GUI + OMR Logic)
├── markscheme.csv       # Automatically generated answer key file
├── student_result.csv   # Output from a single sheet scan
├── batch_results.csv    # Output from batch folder processing
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone [https://github.com/Musab516/OMR-Tool.git](https://github.com/Musab516/OMR-Tool.git)
cd OMR-Tool
```

### 2. Install dependencies

This project relies on OpenCV and NumPy. The Python `csv` and `tkinter` libraries are built-in, but Linux users may need to install the Tkinter system package.

```bash
pip install opencv-python numpy
```

*(For Linux/Ubuntu users only)*
```bash
sudo apt install python3-tk
```

---

## ▶️ Usage

Run the main application file to open the dashboard:

```bash
python main.py
```

### GUI Options:

* **Step 1: Set Markscheme**
  Opens a scrollable window to input the correct answers for Q1 to Q41. Saves to `markscheme.csv`.
* **Step 2: Scan Single Sheet**
  Select a single `.jpg` or `.png` file. It will display the warped image, overlay the extracted ERP, show the score in the UI, and generate a detailed `student_result.csv`.
* **Step 3: Batch Process Folder**
  Select a folder containing multiple OMR images. The tool will process all of them silently and output a compiled `batch_results.csv` containing filenames, ERPs, and scores.

---

## 📊 Output Formats

**Single Scan (`student_result.csv`)**
Provides a granular breakdown of a single student's test.
*Columns: ERP, Question, Detected, Key, Result (Correct/Incorrect/Blank)*

**Batch Processing (`batch_results.csv`)**
Provides a master list of all students in a scanned folder.
*Columns: Filename, ERP, Score (Correct), Wrong, Blank*

---

## 🚧 Calibration Notes

If you are using a different physical OMR sheet design or a different camera, you may need to tweak the coordinate variables inside the `main.py` file. 
* Look for the `=== CALIBRATION SETTINGS ===` blocks inside `extract_erp()` and `detect()` to adjust X/Y starting points and row/column gaps. 
* Setting `draw_debug=True` will draw blue rectangles over the scanning zones to help you align them perfectly.

---

## 👥 Authors

* **Musab Bin Majid**
* **Emad Yar Khan**

---

## ⭐ If you like this project
Give it a star on GitHub!
```