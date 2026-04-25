# OMR Auto Grading Tool

A Python-based Optical Mark Recognition (OMR) system that automatically detects and grades MCQ answer sheets using computer vision.

---

## 🚀 Features

* Detects answers from scanned or photographed MCQ sheets
* Supports **cross-marked answers** (not just filled bubbles)
* Automatic grading using a custom mark scheme
* Batch processing of multiple sheets
* Excel export of results
* Simple GUI for easy use

---

## 🧠 How It Works

1. Image preprocessing (grayscale, thresholding)
2. Detection of answer boxes using contours
3. Extraction of answer column
4. Grouping boxes into questions
5. Adaptive answer detection using image analysis
6. Comparison with mark scheme for grading

---

## 🖥️ GUI Overview

* Create mark scheme using clickable interface
* Grade single image instantly
* Grade multiple sheets (batch mode)
* Export results to Excel

---

## 📁 Project Structure

```
OMR-Tool/
│
├── preprocess.py        # Image preprocessing
├── detect.py            # Detection and answer extraction
├── main.py              # Core pipeline
├── app.py               # GUI application
├── gui_markscheme.py    # Mark scheme creator
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation

### 1. Clone the repository

```
git clone https://github.com/Musab516/OMR-Tool.git
cd OMR-Tool
```

### 2. Install dependencies

```
pip install opencv-python openpyxl
sudo apt install python3-tk
```

---

## ▶️ Usage

### Create Mark Scheme

```
python3 gui_markscheme.py
```

Select correct answers and save.

---

### Run GUI Application

```
python3 app.py
```

Options:

* Grade single image
* Grade folder (batch mode)

---

## 📊 Output

* Instant result popup (single image)
* `results.xlsx` for batch grading

---

## 🔧 Example

```
Detected answers: [1, 1]
Score: 2/2
```

---

## 🚧 Limitations

* Uses a fixed threshold (`y > 250`) for header removal
* Works best with consistent sheet format

---

## 🚀 Future Improvements

* Automatic header detection (remove hardcoding)
* Student ID recognition
* Improved UI design
* PDF support
* Better layout adaptability

---

## 👤 Author

Musab Bin Majid

---

## ⭐ If you like this project

Give it a star on GitHub!
