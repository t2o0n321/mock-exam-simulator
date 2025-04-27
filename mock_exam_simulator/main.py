# mock_exam_simulator/main.py
import tkinter as tk
from .app import MockExamApp

def main():
    root = tk.Tk()
    app = MockExamApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()