from preprocess import preprocess
from detect import detect_boxes, extract_answer_column, group_questions, detect_answers
import json

# -------------------------
# SHARED PIPELINE FUNCTION
# -------------------------
def process_image(path):
    gray, thresh = preprocess(path)

    boxes = detect_boxes(thresh)
    column_boxes = extract_answer_column(boxes)

    # 🔥 CRITICAL FIX
    column_boxes = [b for b in column_boxes if b[1] > 250]

    column_boxes = sorted(column_boxes, key=lambda b: b[1])

    questions = group_questions(column_boxes)

    answers = detect_answers(gray, questions)

    return answers


# -------------------------
# TEST RUN
# -------------------------
if __name__ == "__main__":
    with open("mark_scheme.json") as f:
        ANSWER_KEY = json.load(f)

    IMAGE_PATH = "sheet1.jpg"

    answers = process_image(IMAGE_PATH)

    score = sum(
        1 for i in range(min(len(answers), len(ANSWER_KEY)))
        if answers[i] == ANSWER_KEY[i]
    )

    print("Detected answers:", answers)
    print(f"Score: {score}/{len(ANSWER_KEY)}")