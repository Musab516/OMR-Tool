import cv2
import numpy as np
import csv
import sys

# ================= CONFIG ================= #
ANSWER_KEY = {
    1: 'A', 2: 'B', 3: 'C', 4: 'D', 
} 
# Fallback just so the script doesn't crash if you haven't filled them all in yet:
for i in range(1, 42):
    if i not in ANSWER_KEY:
        ANSWER_KEY[i] = 'A' 

OPTIONS = ['A', 'B', 'C', 'D']

# ================= OMR CLASS ================= #

class OMR:
    def __init__(self, path):
        self.original = cv2.imread(path)
        if self.original is None:
            raise ValueError("Image not found. Please check the file path.")
        
        self.DEBUG = True

    # ---------- HELPER: ORDER POINTS ---------- #
    def order_points(self, pts):
        """Orders 4 points: Top-Left, Top-Right, Bottom-Right, Bottom-Left"""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    # ---------- STEP 1: AUTO SHEET DETECTION (FIDUCIALS) ---------- #
    def get_warped(self):
        img = self.original.copy()
        img_h, img_w = img.shape[:2]
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use adaptive thresholding to find the black squares regardless of lighting
        thresh = cv2.adaptiveThreshold(blurred, 255, 
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 2)

        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        
        # Look for the 4 corner squares
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                area = cv2.contourArea(c)
                
                # Filter for shapes that are square-ish and right size
                if 0.7 <= aspect_ratio <= 1.3 and 200 < area < 5000:
                    M = cv2.moments(c)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        candidates.append([cX, cY])

        if len(candidates) < 4:
            print("WARNING: Could not find 4 corner markers. Using fallback resize.")
            return cv2.resize(img, (800, 1000))

        candidates = np.array(candidates)
        
        # Find the specific markers closest to the 4 corners of the image
        corners = np.array([[0, 0], [img_w, 0], [img_w, img_h], [0, img_h]])
        ordered_markers = []
        
        for corner in corners:
            distances = np.linalg.norm(candidates - corner, axis=1)
            ordered_markers.append(candidates[np.argmin(distances)])
            
        ordered_markers = np.array(ordered_markers, dtype="float32")
        ordered_markers = self.order_points(ordered_markers)

        # Warp based on the centers of the 4 markers
        # Standardizing the output to 800x1000 pixels
        maxW, maxH = 800, 1000
        dst = np.array([
            [0, 0],
            [maxW - 1, 0],
            [maxW - 1, maxH - 1],
            [0, maxH - 1]
        ], dtype="float32")

        M = cv2.getPerspectiveTransform(ordered_markers, dst)
        warped = cv2.warpPerspective(img, M, (maxW, maxH))

        return warped

    # ---------- STEP 2: DARKNESS DETECTION ---------- #
    def get_darkness(self, gray, box):
        x, y, w, h = box
        roi = gray[y:y+h, x:x+w]

        if roi.size == 0:
            return 0

        # UPDATED: Increased threshold to 180 to detect lighter blue ink!
        _, binary = cv2.threshold(roi, 160, 255, cv2.THRESH_BINARY_INV)
        
        filled_pixels = cv2.countNonZero(binary)
        return filled_pixels / float(roi.size)

    # ---------- STEP 3: ANSWER DETECTION ---------- #
    def detect(self):
        warped = self.get_warped()
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

        answers = {}
        q = 1

# ========================================================
        # CALIBRATED COORDINATES
# ========================================================
        LEFT_X = 125   # PERFECT
        RIGHT_X = 480  # PERFECT
        
        # Pushed down by exactly one row (334 + 28) to get off the letters!
        START_Y = 362  
        
        ROW_GAP = 28   # PERFECT
        COL_GAP = 64   # PERFECT

        BOX_W = 24
        BOX_H = 15
# ========================================================

        # LEFT SIDE (Q1–21)
        for i in range(21):
            y = START_Y + int(i * ROW_GAP)
            scores = []
            for j in range(4):
                x = LEFT_X + int(j * COL_GAP)
                
                if self.DEBUG:
                    cv2.rectangle(warped, (x, y), (x + BOX_W, y + BOX_H), (0, 0, 255), 2)
                    
                scores.append(self.get_darkness(gray, (x, y, BOX_W, BOX_H)))

            sorted_scores = sorted(scores, reverse=True)
            
            # Threshold logic for inverted binary pixels
            if sorted_scores[0] > 0.15 and (sorted_scores[0] - sorted_scores[1]) > 0.04:
                answers[q] = OPTIONS[np.argmax(scores)]
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

            if sorted_scores[0] > 0.4 and (sorted_scores[0] - sorted_scores[1]) > 0.15:
                answers[q] = OPTIONS[np.argmax(scores)]
            else:
                answers[q] = None
            q += 1

        return answers, warped

# ================= SCORING ================= #

def evaluate(answers):
    correct, wrong, blank = 0, 0, 0

    for i in range(1, 42):
        if answers.get(i) is None:
            blank += 1
        elif answers.get(i) == ANSWER_KEY.get(i):
            correct += 1
        else:
            wrong += 1

    return correct, wrong, blank

# ================= MAIN ================= #

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 main.py image.jpg")
        sys.exit()

    path = sys.argv[1]

    omr = OMR(path)
    answers, warped = omr.detect()

    correct, wrong, blank = evaluate(answers)

    print("\n===== RESULT =====")
    for i in range(1, 42):
        print(f"Q{i:2d}: {answers.get(i)}")

    print("\n===== SCORE =====")
    print(f"Correct: {correct}")
    print(f"Wrong  : {wrong}")
    print(f"Blank  : {blank}")
    print(f"Score  : {correct}/41")

    # Save CSV
    with open("result.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Q" + str(i) for i in range(1, 42)])
        writer.writerow([answers.get(i) for i in range(1, 42)])

    cv2.imshow("Warped Sheet (Press any key to close)", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()