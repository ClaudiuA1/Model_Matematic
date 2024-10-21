import tkinter as tk

class ToolbarManager:
    def __init__(self, parent, canvas_manager):
        self.canvas_manager = canvas_manager
        
        # Crearea toolbar-ului
        self.toolbar = tk.Frame(parent, bg="lightgrey", bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.clear_button = tk.Button(
            self.toolbar,
            text="Clear All",
            command=self.canvas_manager.clear_all,
            background="red",
            font="Calibri",
        )
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.calculate_button = tk.Button(self.toolbar, text="Calculate")
        self.calculate_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Crearea elementelor din toolbar
        self.create_toolbar_item("Resistor", "resistor.png")
        self.create_toolbar_item("Capacitor", "capacitor.png")
        self.create_toolbar_item("Inductor", "inductor.png")

    def create_toolbar_item(self, name, image_file):
        label = tk.Label(self.toolbar, text=name, bg="lightgrey", padx=10, pady=5)
        label.pack(side=tk.LEFT, padx=5, pady=5)
        label.bind("<Button-1>", self.canvas_manager.on_drag_start)
        label.bind("<B1-Motion>", self.canvas_manager.on_drag_motion)
        label.bind("<ButtonRelease-1>", self.canvas_manager.on_drag_end)
        label.image_file = image_file

