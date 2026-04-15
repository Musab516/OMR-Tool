import cv2

# -------------------------
# STEP 1: detect boxes
# -------------------------
def detect_boxes(thresh):
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    boxes = []

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)

        aspect_ratio = w / float(h)
        
        # 🔥 FIX 1: Bounding box area is completely immune to broken contour lines
        bbox_area = w * h

        if 15 < w < 60 and 15 < h < 60:
            if 0.70 < aspect_ratio < 1.30:
                if 200 < bbox_area < 3600:
                    boxes.append((x, y, w, h, c))

    return boxes

# -------------------------
# STEP 2: find answer column
# -------------------------
def extract_answer_column(boxes):
    if not boxes:
        return []

    # sort by x
    boxes = sorted(boxes, key=lambda b: b[0])

    # take first few boxes to estimate left column
    sample = boxes[:10]
    avg_x = sum(b[0] for b in sample) / len(sample)

    left_boxes = []

    for (x, y, w, h, c) in boxes:
        # -25 heavily restricts the left side (blocks text labels)
        # +80 allows drift to the right side (handles slanted paper)
        if -25 < (x - avg_x) < 80:   
            left_boxes.append((x, y, w, h, c))

    return left_boxes
# -------------------------
# STEP 3: group questions
# -------------------------
def group_questions(column_boxes):
    # sort top to bottom
    column_boxes = sorted(column_boxes, key=lambda b: b[1])

    questions = []

    i = 0
    while i + 3 < len(column_boxes):
        q = column_boxes[i:i+4]
        questions.append(q)
        i += 4

    return questions

# -------------------------
# STEP 4: detect answers
# -------------------------

def detect_answers(gray, questions):
    answers = []

    for q in questions:
        scores = []

        for (x, y, w, h, c) in q:
            M = cv2.moments(c)

            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx = x + w // 2
                cy = y + h // 2

            # sample small region around center
            r = int(min(w, h) * 0.25)

            roi = gray[
                cy - r : cy + r,
                cx - r : cx + r
            ]

            if roi.size == 0:
                scores.append(0)
                continue

            mean_val = cv2.mean(roi)[0]
            score = 255 - mean_val

            scores.append(score)

        print("final scores:", scores)

        selected = scores.index(max(scores))
        answers.append(selected)

    return answers