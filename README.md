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