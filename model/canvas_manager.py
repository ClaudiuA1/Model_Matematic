import tkinter as tk
from PIL import Image, ImageTk

class CanvasManager:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, bg="white", width=600, height=600)
        self.canvas.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

        self.dragging_data = {
            "item": None,
            "x": 0,
            "y": 0,
            "offset_x": 0,
            "offset_y": 0,
        }
        self.item_id_counter = 0
        self.connections = []
        self.connection_start = None
        self.temp_connection = None
        self.item_connection_points = {}
        self.images = []

        # Legarea evenimentelor de canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)

    def on_drag_start(self, event):
        widget = event.widget
        self.dragging_data["item"] = widget.image_file
        self.dragging_data["x"] = event.x_root
        self.dragging_data["y"] = event.y_root
        canvas_x = self.canvas.canvasx(event.x_root - self.canvas.winfo_rootx())
        canvas_y = self.canvas.canvasy(event.y_root - self.canvas.winfo_rooty())
        self.dragging_data["offset_x"] = event.x_root - canvas_x
        self.dragging_data["offset_y"] = event.y_root - canvas_y

    def on_drag_motion(self, event):
        mouse_x = self.canvas.canvasx(event.x_root - self.canvas.winfo_rootx())
        mouse_y = self.canvas.canvasy(event.y_root - self.canvas.winfo_rooty())
        new_x = mouse_x - self.dragging_data["offset_x"]
        new_y = mouse_y - self.dragging_data["offset_y"]
        self.canvas.delete("dragging")
        self.draw_image(new_x, new_y, self.dragging_data["item"], tag="dragging")

    def on_drag_end(self, event):
        final_x = self.canvas.canvasx(event.x_root - self.canvas.winfo_rootx()) - self.dragging_data["offset_x"]
        final_y = self.canvas.canvasy(event.y_root - self.canvas.winfo_rooty()) - self.dragging_data["offset_y"]
        item_id = f"item{self.item_id_counter}"
        self.item_id_counter += 1
        self.canvas.delete("dragging")
        self.draw_image(final_x, final_y, self.dragging_data["item"], tag=item_id)
        self.create_connection_points(final_x, final_y, item_id)
        self.reset_dragging_data()

    def draw_image(self, x, y, image_file, tag):
        image = self.load_image(image_file, 50, 30)
        image_id = self.canvas.create_image(x, y, anchor=tk.NW, image=image, tags=tag)
        self.canvas.tag_lower(image_id)
        self.images.append(image)

    def load_image(self, image_file, width, height):
        image = Image.open(image_file)
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def create_connection_points(self, x, y, item_id):
        image_width = 50
        image_height = 30
        left_x = x - 5
        left_y = y + image_height // 2
        right_x = x + image_width
        right_y = y + image_height // 2

        point_radius = 5
        left_point = self.canvas.create_oval(
            left_x - point_radius, left_y - point_radius,
            left_x + point_radius, left_y + point_radius,
            fill="red", tags=(item_id, "connection_point")
        )
        right_point = self.canvas.create_oval(
            right_x - point_radius, right_y - point_radius,
            right_x + point_radius, right_y + point_radius,
            fill="red", tags=(item_id, "connection_point")
        )

        self.item_connection_points[item_id] = {'left_point': left_point, 'right_point': right_point}

        self.canvas.tag_bind(left_point, '<Enter>', lambda e: self.canvas.itemconfig(left_point, fill="gray"))
        self.canvas.tag_bind(left_point, '<Leave>', lambda e: self.canvas.itemconfig(left_point, fill="red"))
        self.canvas.tag_bind(right_point, '<Enter>', lambda e: self.canvas.itemconfig(right_point, fill="gray"))
        self.canvas.tag_bind(right_point, '<Leave>', lambda e: self.canvas.itemconfig(right_point, fill="red"))

    def on_canvas_click(self, event):
        clicked_items = self.canvas.find_withtag("current")
        if clicked_items:
            if "connection_point" in self.canvas.gettags(clicked_items[0]):
                self.select_connection_point(clicked_items[0])
            elif self.canvas.type(clicked_items[0]) == 'line':
                self.select_connection_line(clicked_items[0])

    def select_connection_point(self, point):
        if self.connection_start is None:
            self.connection_start = point
            self.canvas.itemconfig(point, fill="blue")
        else:
            self.end_connection(point)

    def select_connection_line(self, line_id):
        if hasattr(self, 'selected_connection_line'):
            self.canvas.itemconfig(self.selected_connection_line, fill="black")
        self.selected_connection_line = line_id
        self.canvas.itemconfig(line_id, fill="red")

    def delete_selected_connection(self):
        if hasattr(self, 'selected_connection_line'):
            self.canvas.delete(self.selected_connection_line)
            self.connections.remove(self.selected_connection_line)
            del self.selected_connection_line

    def on_canvas_motion(self, event):
        if self.connection_start:
            if not hasattr(self, 'last_x') or not hasattr(self, 'last_y'):
                self.last_x, self.last_y = event.x, event.y
            if abs(event.x - self.last_x) > 4 or abs(event.y - self.last_y) > 4:
                self.draw_temp_connection(event.x, event.y)
                self.last_x, self.last_y = event.x, event.y

    def draw_temp_connection(self, x, y):
        if self.connection_start:
            if self.temp_connection:
                self.canvas.delete(self.temp_connection)
            start_coords = self.canvas.coords(self.connection_start)
            if start_coords:
                x1, y1 = (start_coords[0] + start_coords[2]) / 2, (start_coords[1] + start_coords[3]) / 2
                self.temp_connection = self.canvas.create_line(x1, y1, x, y, fill="black", width=2)

    def end_connection(self, end_point):
        if self.connection_start and self.connection_start != end_point:
            start_coords = self.canvas.coords(self.connection_start)
            end_coords = self.canvas.coords(end_point)
            if start_coords and end_coords:
                x1, y1 = (start_coords[0] + start_coords[2]) / 2, (start_coords[1] + start_coords[3]) / 2
                x2, y2 = (end_coords[0] + end_coords[2]) / 2, (end_coords[1] + end_coords[3]) / 2
                self.draw_rectangular_connection((x1, y1), (x2, y2))

        if self.connection_start:
            self.canvas.itemconfig(self.connection_start, fill="red")
        self.canvas.itemconfig(end_point, fill="red")
        self.connection_start = None
        if self.temp_connection:
            self.canvas.delete(self.temp_connection)
            self.temp_connection = None

    def draw_rectangular_connection(self, start_coords, end_coords):
        x1, y1 = start_coords
        x2, y2 = end_coords

        line1 = self.canvas.create_line(x1, y1, (x1 + x2) / 2, y1, fill="black", width=2)
        line2 = self.canvas.create_line((x1 + x2) / 2, y1, (x1 + x2) / 2, y2, fill="black", width=2)
        line3 = self.canvas.create_line((x1 + x2) / 2, y2, x2, y2, fill="black", width=2)

        self.connections.extend([line1, line2, line3])

    def clear_all(self):
        self.canvas.delete("all")
        self.connections = []
        self.item_connection_points = {}
        self.connection_start = None
        self.temp_connection = None
        self.images.clear()

    def reset_dragging_data(self):
        self.dragging_data = {
            "item": None,
            "x": 0,
            "y": 0,
            "offset_x": 0,
            "offset_y": 0,
        }