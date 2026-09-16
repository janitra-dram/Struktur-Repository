import tkinter as tk
from frontend.ui import AppUI

if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    app.run()
