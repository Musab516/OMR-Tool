import cv2
import numpy as np
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# ================= OMR CLASS ================= #

class OMR:
    def __init__(self, path):
        self.original = cv2.imread(path)
        if self.original is None:
            raise ValueError("Image not found. Please check the file path.")
        self.DEBUG = True
        self.OPTIONS = ['A', 'B', 'C', 'D']

    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def get_warped(self):
        img = self.original.copy()
        img_h, img_w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                area = cv2.contourArea(c)
                if 0.7 <= aspect_ratio <= 1.3 and 200 < area < 5000:
                    M = cv2.moments(c)
                    if M["m00"] != 0:
                        candidates.append([int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])])

        if len(candidates) < 4:
            return cv2.resize(img, (800, 1000))

        candidates = np.array(candidates)
        corners = np.array([[0, 0], [img_w, 0], [img_w, img_h], [0, img_h]])
        ordered_markers = self.order_points(np.array([candidates[np.argmin(np.linalg.norm(candidates - c, axis=1))] for c in corners], dtype="float32"))

        maxW, maxH = 800, 1000
        dst = np.array([[0, 0], [maxW - 1, 0], [maxW - 1, maxH - 1], [0, maxH - 1]], dtype="float32")
        M = cv2.getPerspectiveTransform(ordered_markers, dst)
        return cv2.warpPerspective(img, M, (maxW, maxH))

    def get_darkness(self, gray, box):
        x, y, w, h = box
        roi = gray[y:y+h, x:x+w]
        if roi.size == 0: return 0
        _, binary = cv2.threshold(roi, 160, 255, cv2.THRESH_BINARY_INV) 
        return cv2.countNonZero(binary) / float(roi.size)

    def detect(self):
        warped = self.get_warped()
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        answers = {}
        
        # YOUR CALIBRATED COORDINATES
        LEFT_X = 125   
        RIGHT_X = 480  
        START_Y = 362  
        ROW_GAP = 28   
        COL_GAP = 64   
        BOX_W, BOX_H = 24, 15

        # LEFT SIDE (Q1–21)
        q = 1
        for i in range(21):
            y = START_Y + int(i * ROW_GAP)
            scores = []
            for j in range(4):
                x = LEFT_X + int(j * COL_GAP)
                if self.DEBUG:
                    cv2.rectangle(warped, (x, y), (x + BOX_W, y + BOX_H), (0, 0, 255), 2)
                scores.append(self.get_darkness(gray, (x, y, BOX_W, BOX_H)))

            sorted_scores = sorted(scores, reverse=True)
            if sorted_scores[0] > 0.15 and (sorted_scores[0] - sorted_scores[1]) > 0.04:
                answers[q] = self.OPTIONS[np.argmax(scores)]
            else:
                answers[q] = None
            q += 1

        # RIGHT SIDE (Q22–41)
        for i in range(20):
            y = START_Y + int(i * ROW_GAP)
            scores = []
            for j in range(4):
                x = RIGHT_X + int(j * COL_GAP)
                if self.DEBUG:
                    cv2.rectangle(warped, (x, y), (x + BOX_W, y + BOX_H), (0, 0, 255), 2)
                scores.append(self.get_darkness(gray, (x, y, BOX_W, BOX_H)))

            sorted_scores = sorted(scores, reverse=True)
            if sorted_scores[0] > 0.15 and (sorted_scores[0] - sorted_scores[1]) > 0.04:
                answers[q] = self.OPTIONS[np.argmax(scores)]
            else:
                answers[q] = None
            q += 1

        return answers, warped

# ================= GUI INTERFACE & LOGIC ================= #

class OMRDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("OMR Evaluation System")
        self.root.geometry("450x450")
        self.ms_path = "markscheme.csv"

        tk.Label(root, text="OMR Scanner Interface", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Button(root, text="Step 1: Set Markscheme", command=self.open_markscheme, width=30, height=2).pack(pady=10)
        tk.Button(root, text="Step 2: Scan Single Sheet", command=self.process_sheet, width=30, height=2, bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(root, text="Step 3: Batch Process Folder", command=self.batch_process, width=30, height=2, bg="#FF9800", fg="white").pack(pady=10)
        
        self.status_var = tk.StringVar(value="Status: Ready")
        tk.Label(root, textvariable=self.status_var, font=("Arial", 10, "italic")).pack(pady=20)

    def extract_erp(self, omr_instance, warped, draw_debug=False):
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        
        # === CALIBRATION SETTINGS ===
        ERP_START_X = 184    # Your perfect starting X
        ERP_START_Y = 158    # Your perfect starting Y
        
        ERP_COL_GAP = 58     # Gap between normal columns (e.g., 0 to 1, or 5 to 6)
        ERP_ROW_GAP = 30     # Your perfect vertical gap
        
        # THE MISSING PIECE: The extra physical distance between block 4 and block 5
        EXTRA_GAP_AFTER_4 = 15 # <-- Tweak this number to push the 5-9 block to the right!
        
        ERP_DIGITS = 5       
        BOX_W, BOX_H = 24, 15
        # ============================

        erp = ""
        digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        for row in range(ERP_DIGITS):
            scores = []
            for col in range(10): 
                
                # Base X coordinate calculation
                x = ERP_START_X + int(col * ERP_COL_GAP)
                
                # If we have reached column 5 or higher, add the extra physical jump!
                if col >= 5:
                    x += EXTRA_GAP_AFTER_4
                    
                y = ERP_START_Y + int(row * ERP_ROW_GAP)
                
                if draw_debug:
                    cv2.rectangle(warped, (x, y), (x + BOX_W, y + BOX_H), (255, 0, 0), 2)
                    
                scores.append(omr_instance.get_darkness(gray, (x, y, BOX_W, BOX_H)))

            sorted_scores = sorted(scores, reverse=True)
            if sorted_scores[0] > 0.15 and (sorted_scores[0] - sorted_scores[1]) > 0.04:
                erp += digits[np.argmax(scores)]
            else:
                erp += "?" 

        return erp
    
    def open_markscheme(self):
        ms_win = tk.Toplevel(self.root)
        ms_win.title("Edit Markscheme")
        ms_win.geometry("400x600")

        container = tk.Frame(ms_win)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        current_key = {}
        if os.path.exists(self.ms_path):
            with open(self.ms_path, "r") as f:
                reader = csv.reader(f)
                current_key = {row[0]: row[1] for row in reader if row}

        vars_dict = {}
        for i in range(1, 42):
            row_frame = tk.Frame(scrollable_frame)
            row_frame.pack(fill="x", padx=20, pady=5)
            
            tk.Label(row_frame, text=f"Q{i:02d}:", width=6, font=("Arial", 10, "bold")).pack(side="left")
            
            v = tk.StringVar(value=current_key.get(str(i), "A"))
            vars_dict[i] = v
            for opt in ['A', 'B', 'C', 'D']:
                tk.Radiobutton(row_frame, text=opt, variable=v, value=opt, padx=5).pack(side="left")

        def save_and_close():
            canvas.unbind_all("<MouseWheel>")
            with open(self.ms_path, "w", newline="") as f:
                writer = csv.writer(f)
                for q, var in vars_dict.items():
                    writer.writerow([q, var.get()])
            messagebox.showinfo("Success", "Markscheme saved successfully!")
            ms_win.destroy()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        save_btn = tk.Button(ms_win, text="SAVE MARKSCHEME", command=save_and_close, 
                             bg="#2196F3", fg="white", font=("Arial", 10, "bold"), height=2)
        save_btn.pack(fill="x")

    def process_sheet(self):
        if not os.path.exists(self.ms_path):
            messagebox.showwarning("Missing Key", "Please set the markscheme first.")
            return

        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if not file_path:
            return

        with open(self.ms_path, "r") as f:
            reader = csv.reader(f)
            answer_key = {int(row[0]): row[1] for row in reader if row}

        try:
            omr = OMR(file_path)
            detected_answers, warped = omr.detect() # Original detect method used here
            
            # Extract ERP externally using the warped image
            erp = self.extract_erp(omr, warped, draw_debug=True)

            correct, wrong, blank = 0, 0, 0
            for i in range(1, 42):
                ans = detected_answers.get(i)
                key = answer_key.get(i)
                if ans is None: blank += 1
                elif ans == key: correct += 1
                else: wrong += 1

            self.status_var.set(f"ERP: {erp} | Score: {correct}/41 | Wrong: {wrong} | Blank: {blank}")
            
            with open("student_result.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ERP", "Question", "Detected", "Key", "Result"])
                for i in range(1, 42):
                    res = "Correct" if detected_answers.get(i) == answer_key.get(i) else "Incorrect"
                    if detected_answers.get(i) is None: res = "Blank"
                    writer.writerow([erp, i, detected_answers.get(i), answer_key.get(i), res])

            # Label the image with the extracted ERP
            cv2.putText(warped, f"ERP: {erp}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            cv2.imshow("Warped View (Press any key to close)", warped)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")

    def batch_process(self):
        if not os.path.exists(self.ms_path):
            messagebox.showwarning("Missing Key", "Please set the markscheme first.")
            return

        folder_path = filedialog.askdirectory(title="Select Folder Containing OMR Sheets")
        if not folder_path:
            return

        with open(self.ms_path, "r") as f:
            reader = csv.reader(f)
            answer_key = {int(row[0]): row[1] for row in reader if row}

        output_csv = os.path.join(folder_path, "batch_results.csv")
        valid_extensions = {".jpg", ".jpeg", ".png"}
        
        processed_count = 0
        error_count = 0

        self.status_var.set("Processing batch... please wait.")
        self.root.update()

        try:
            with open(output_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Filename", "ERP", "Score (Correct)", "Wrong", "Blank"])

                for filename in os.listdir(folder_path):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in valid_extensions:
                        file_path = os.path.join(folder_path, filename)
                        try:
                            omr = OMR(file_path)
                            omr.DEBUG = False # Disable debug drawing for speed
                            detected_answers, warped = omr.detect()
                            
                            # Extract ERP purely behind the scenes
                            erp = self.extract_erp(omr, warped, draw_debug=False)

                            correct, wrong, blank = 0, 0, 0
                            for i in range(1, 42):
                                ans = detected_answers.get(i)
                                key = answer_key.get(i)
                                if ans is None: blank += 1
                                elif ans == key: correct += 1
                                else: wrong += 1

                            writer.writerow([filename, erp, correct, wrong, blank])
                            processed_count += 1
                            
                        except Exception as e:
                            print(f"Error processing {filename}: {e}")
                            writer.writerow([filename, "ERROR", "", "", ""])
                            error_count += 1

            self.status_var.set(f"Batch Done! Processed: {processed_count} | Errors: {error_count}")
            messagebox.showinfo("Batch Complete", f"Successfully processed {processed_count} files.\nResults saved to:\n{output_csv}")

        except Exception as e:
            messagebox.showerror("Batch Error", f"An error occurred during batch processing: {str(e)}")
            self.status_var.set("Status: Batch processing failed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = OMRDashboard(root)
    root.mainloop()