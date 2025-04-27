# mock_exam_simulator/__main__.py
import tkinter as tk
from .app import MockExamApp

def main():
    root = tk.Tk()
    app = MockExamApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()