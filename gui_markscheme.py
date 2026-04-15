import tkinter as tk
import json

answers = []

def select_option(q, opt, buttons):
    answers[q] = opt

    for i, b in enumerate(buttons):
        b.config(bg="green" if i == opt else "SystemButtonFace")

def save():
    with open("mark_scheme.json", "w") as f:
        json.dump(answers, f)

    print("Saved mark_scheme.json")

def build(n=5):
    global answers
    answers = [-1] * n

    root = tk.Tk()
    root.title("Mark Scheme")

    for q in range(n):
        tk.Label(root, text=f"Q{q+1}").grid(row=q, column=0)

        btns = []

        for i in range(4):
            b = tk.Button(root, text=chr(65+i), width=5)
            b.grid(row=q, column=i+1)

            b.config(command=lambda q=q, i=i, btns=btns: select_option(q, i, btns))
            btns.append(b)

    tk.Button(root, text="Save", command=save).grid(row=n+1, column=0)

    root.mainloop()

if __name__ == "__main__":
    build(2)  # change number of questions