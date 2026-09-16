import tkinter as tk

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        
        # Minimal UI implementation
        self.label = tk.Label(root, text="2EZ4U Food Delivery - M1 Pesanan")
        self.label.pack(pady=20)

    def run(self):
        self.root.mainloop()
