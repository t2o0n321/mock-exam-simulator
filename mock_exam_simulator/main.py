import tkinter as tk
from .app import MockExamApp

def main() -> None:
    """Run the mock exam simulator."""
    root = tk.Tk()
    app = MockExamApp(root)
    root.mainloop()
