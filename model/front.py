import tkinter as tk
from PIL import Image, ImageTk
from canvas_manager import CanvasManager
from tool_bar_manager import ToolbarManager


class CircuitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Circuit Designer")
        self.root.geometry("800x800")

        self.canvas_manager = CanvasManager(root)
        self.toolbar_manager = ToolbarManager(root, self.canvas_manager)

        self.root.bind("<BackSpace>", self.handle_backspace)

    def handle_backspace(self, event):
        self.canvas_manager.delete_selected_connection()

root = tk.Tk()
app = CircuitApp(root)
root.mainloop()
