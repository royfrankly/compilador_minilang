import tkinter as tk
from src.ui.app_window import CompiladorApp

if __name__ == "__main__":
    root = tk.Tk()
    app = CompiladorApp(root)
    root.mainloop()