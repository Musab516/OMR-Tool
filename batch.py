import os
import json
from openpyxl import Workbook

from preprocess import preprocess
from detect import detect_boxes, extract_answer_column, group_questions, detect_answers

# load mark scheme
with open("mark_scheme.json") as f:
    ANSWER_KEY = json.load(f)

INPUT_FOLDER = "sheets"


def process_sheet(path):
    gray, thresh = preprocess(path)

    boxes = detect_boxes(thresh)
    column_boxes = extract_answer_column(boxes)

    # remove header junk
    column_boxes = sorted(column_boxes, key=lambda b: b[1])[2:]

    questions = group_questions(column_boxes)

    answers = detect_answers(gray, questions)

    # grading
    score = 0
    for i in range(min(len(answers), len(ANSWER_KEY))):
        if answers[i] == ANSWER_KEY[i]:
            score += 1

    return answers, score


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    # header
    header = ["File"] + [f"Q{i+1}" for i in range(len(ANSWER_KEY))] + ["Score"]
    ws.append(header)

    for file in os.listdir(INPUT_FOLDER):
        if file.lower().endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(INPUT_FOLDER, file)

            print(f"Processing {file}...")

            answers, score = process_sheet(path)

            row = [file] + answers + [score]
            ws.append(row)

    wb.save("results.xlsx")
    print("✅ results.xlsx created")


if __name__ == "__main__":
    main()