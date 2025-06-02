# Licensed under the MIT License

import sys
import importlib.util
import tkinter as tk
import ctypes

from PIL import Image, ImageDraw, ImageTk

from structtkinter.styles import *
from structtkinter.documents import *

class Tag():
    tag_type = "Tag"

    background_color = "transparent"
    border_bottom_left_radius = 0
    border_bottom_right_radius = 0
    border_top_left_radius = 0
    border_top_right_radius = 0
    height = "fit-content"
    width = "100%"

    def __init__(self, children: list = [], classes: list = [], id: str = "", style: Style = Style()):
        if not isinstance(children, list):
            raise TypeError("children must be a list")
        if not all(isinstance(child, Tag) for child in children):
            raise TypeError("all children must be instances of Tag")
        if not isinstance(classes, list):
            raise TypeError("classes must be a list")
        if not all(isinstance(class_name, str) for class_name in classes):
            raise TypeError("all classes must be strings")
        if not isinstance(id, str):
            raise TypeError("id must be a string")
        if not isinstance(style, Style):
            raise TypeError("style must be an instance of Style")

        self.parent = "not defined"
        self.children = children
        self.classes = classes
        self.id = id

        self.style = style
        self.stylize()
        self._set_attributes()

    def stylize(self):
        global styles
        styles_names = list(styles.keys())

        if "#"+self.id in styles_names:
            self.style += styles["#"+self.id]

        for class_name in self.classes:
            class_name = "." + class_name
            if class_name in styles_names:
                self.style += styles[class_name]

        if self.tag_type.lower() in styles_names:
            self.style += styles[self.tag_type.lower()]

    def _set_attributes(self):
        self.background_color = self.style.background_color if self.style.background_color != None else "transparent"

        self.border_bottom_left_radius = self.style.border_bottom_left_radius if self.style.border_bottom_left_radius != None else 0
        self.border_bottom_right_radius = self.style.border_bottom_right_radius if self.style.border_bottom_right_radius != None else 0
        self.border_top_left_radius = self.style.border_top_left_radius if self.style.border_top_left_radius != None else 0
        self.border_top_right_radius = self.style.border_top_right_radius if self.style.border_top_right_radius != None else 0

        self.height = self.style.height if self.style.height != None else "fit-content"
        self.width = self.style.width if self.style.width != None else "100%"

        self._set_tag_attributes()

    def _set_tag_attributes(self):
        return

    def _get_value(self, attribute: str, came_from: str = ""):
        if attribute == "width":
            value = self.width
            positional_counterpart = "x"
        elif attribute == "height":
            value = self.height
            positional_counterpart = "y"
        elif attribute == "x":
            return self.x
        elif attribute == "y":
            return self.y

        if isinstance(value, str):
            if value[-1] == "%":
                if came_from != "parent":
                    parent_value = self.parent._get_value(attribute, came_from="child")
                    return int(value[:-1]) * parent_value / 100
                else:
                    return 0
            elif value == "fit-content":
                max_position = 0
                min_position = None
                for child in self.children:
                    if came_from != "child":
                        max_position = max(child._get_value(positional_counterpart) + child._get_value(attribute, came_from="parent"), max_position)
                        min_position = min(child._get_value(positional_counterpart), min_position) if min_position != None else child._get_value(positional_counterpart)
                    else:
                        return 0
                min_position = 0 if min_position == None else min_position
                return max_position - min_position
            else:
                return int(value)
        return value

    def _place(self, x, y):
        self.x = x
        self.y = y

        width = self._get_value("width")
        height = self._get_value("height")

        r1 = min(self.border_top_right_radius, min(height / 2, width / 2))
        r2 = min(self.border_top_left_radius, min(height / 2, width / 2))
        r3 = min(self.border_bottom_left_radius, min(height / 2, width / 2))
        r4 = min(self.border_bottom_right_radius, min(height / 2, width / 2))

        x1, y1 = self.x, self.y
        x2, y2 = self.x + width, self.y + height
        draw_command = {"type": "box", "kwargs": {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "r1": r1, "r2": r2, "r3": r3, "r4": r4, "fill": self.background_color, "tag": ("mouse")}}

        return draw_command

    def add_to_document(self):
        global document
        document.add_element(self)

    def _execute_children(self, x, y):
        draw_commands = []
        for child in self.children:
            if isinstance(child, Tag):
                child.parent = self
                child.add_to_document()
                draw_commands_child = child._execute_children(x=0, y=y)
                draw_commands.append(child._place(x=0, y=y))
                draw_commands.extend(draw_commands_child)
                y += child._get_value("height")
            elif isinstance(child, Script):
                child._load_script()

        return draw_commands

    def __repr__(self):
        repr = f"{self.tag_type}("
        repr += f"classes={self.classes}" if self.classes != [] else ""
        repr += f", id={self.id}" if self.id != "" else ""
        repr += ")"
        return repr

class STk(Tag):
    tag_type = "STk"
    def __init__(self, children: list = [], classes: list = [], id: str = "", style: Style = Style()):
        super().__init__(children, classes=classes, id=id, style=style)

        # Variables
        self.draw_commands = []
        self.parent = None

        # Create the main window
        self.tk = tk.Tk()
        self.tk.configure(bg=self.background_color)
        self.x = int((screen_width - self.width) / 2)
        self.y = int((screen_height*4/5 - self.height) / 2)
        self.tk.geometry(f"{self.width}x{int(self.height)}+{self.x}+{self.y}")

        # Add itselft to the document
        global document
        document.add_element(self)

        # Execute
        self._execute_children()
        self._place()

    def _set_tag_attributes(self):
        self.background_color = self.style.background_color if self.style.background_color != None else "white"

        self.height = self.style.height if self.style.height != None else 250
        self.width = self.style.width if self.style.width != None else 300

    def _place(self):
        # Get the maximum x and y values
        max_x = 0
        max_y = 0
        for draw_command in self.draw_commands:
            if draw_command["type"] == "box":
                x2 = draw_command["kwargs"]["x2"]
                y2 = draw_command["kwargs"]["y2"]
                if x2 > max_x:
                    max_x = x2
                if y2 > max_y:
                    max_y = y2

        # Create canvas
        self.canvas = tk.Canvas(master=self.tk, bd=0, bg=self.background_color, borderwidth=0, highlightthickness=0, width=max_x, height=max_y)
        self.canvas.pack(anchor="w")

        # Run draw commands
        for draw_command in self.draw_commands:
            if draw_command["type"] == "box":
                self.__draw_box(**draw_command["kwargs"])

        # Run the program
        self.tk.mainloop()

    def _execute_children(self):
        y = 0
        for child in self.children:
            child.parent = self
            child.add_to_document()
            draw_commands = child._execute_children(x=0, y=y)
            self.draw_commands.append(child._place(x=0, y=y))
            self.draw_commands.extend(draw_commands)
            y += child._get_value("height")
            if isinstance(child, Script):
                child._load_script()

    def __draw_box(self, x1, y1, x2, y2, r1, r2, r3, r4, fill, tag=None, scale=2):
        """
        Draws a rectangle with cut corners onto a canvas.

        Parameters:
        - canvas: Tkinter Canvas to draw on.
        - x1, y1, x2, y2: corner coordinates of the outer rectangle (in canvas pixels).
        - r1, r2, r3, r4: corner radii (in canvas pixels), in this order:
            r1 = top-right radius
            r2 = top-left radius
            r3 = bottom-left radius
            r4 = bottom-right radius
        - fill:   fill color (any Tk- or PIL-compatible color, e.g. "#RRGGBB").
        - tag:    optional tag (string or tuple of strings) to assign to the final image.
        - scale:  integer supersampling factor (e.g. 4 or 8). Higher = smoother edges.

        This function does NOT draw multiple canvas items. Instead, it:
        1. Creates one large (w*scale, h*scale) RGBA PIL image.
        2. Draws the five filled rectangles (four for each side of the box and one for the center)
            and four filled quarter-circles (to carve out each rounded corner).
        3. Downsamples that big image back to (w, h) with Lanczos filtering.
        4. Converts to an ImageTk.PhotoImage and places it at (0, 0) on the canvas.

        Usage example:
            create_box_cut_corners(my_canvas,
                                x1=50, y1=50, x2=250, y2=250,
                                r1=30, r2=20, r3=40, r4=15,
                                fill="#88CCFF", tag="bluebox",
                                scale=4)
        """

        if fill == "transparent":
            return

        # Ensure the canvas has its actual on-screen size:
        self.canvas.update_idletasks()
        w = self.canvas.winfo_reqwidth()
        h = self.canvas.winfo_reqheight()
        s = scale  # alias

        # Make one high-res RGBA image (transparent background):
        hi_res_img = Image.new("RGBA", (w * s, h * s), (255, 255, 255, 0))
        draw = ImageDraw.Draw(hi_res_img)

        # Get the biggest radius for each side of the box
        rt = max(r1, r2) # radius top
        rl = max(r2, r3) # radius left
        rb = max(r3, r4) # radius bottom
        rr = max(r4, r1) # radius right

        # Draw the five rectangles (one for each side of the box and one for the center):
        rectangles = [
            ((x2-rr, y1+r1), (x2,    y2-r4)), # right
            ((x1+r2, y1   ), (x2-r1, y1+rt)), # top
            ((x1   , y1+r2), (x1+rl, y2-r3)), # left
            ((x1+r3, y2-rb), (x2-r4, y2   )), # bottom
            ((x1+rl, y1+rt), (x2-rr, y2-rb)), # center
        ]
        for (xs, ys), (xe, ye) in rectangles:
            if xs < xe and ys < ye:
                draw.rectangle(
                    [xs * s, ys * s, xe * s, ye * s],
                    fill=fill,
                    outline=None
                )

        # Draw four corners:
        def _tk_to_pil(start_ccw, extent_ccw):
            """
            Convert a Tk "start CCW from +x" and an extent (positive CCW)
            into PIL's [start, end] measured CW.
            """

            start = -start_ccw
            if extent_ccw >= 0:
                end = start
                start = start - extent_ccw
            else:
                end = start - extent_ccw
            return start, end

        corners = [
            (  0, (x2-2*r1, y1     ), r1), # top-right quadrant
            ( 90, (x1,      y1     ), r2), # top-left quadrant
            (180, (x1,      y2-2*r3), r3), # bottom-left quadrant
            (270, (x2-2*r4, y2-2*r4), r4), # bottom-right quadrant
        ]
        for start, (xa, ya), r in corners:
            if r <= 0:
                continue
            # convert to PIL angles:
            start, end = _tk_to_pil(start, 90)
            # build PIL bounding box, scaled by s:
            x0 = xa * s
            y0 = ya * s
            x1 = (xa + 2*r) * s
            y1 = (ya + 2*r) * s
            # draw a filled pieslice (quarter-circle) in that box:
            draw.pieslice(
                [x0, y0, x1, y1],
                start=start, end=end,
                fill=fill,
                outline=None
            )

        # Downsample with a Lanczos filter -> final smooth image
        smooth_img = hi_res_img.resize((w, h), resample=Image.LANCZOS)
        photo = ImageTk.PhotoImage(smooth_img)

        # Draw on the canvas
        self.canvas.create_image(0, 0, anchor="nw", image=photo, tags=(tag,) if isinstance(tag, str) else (tag or ()))

        # Keep a reference so the PhotoImage isn't garbage‐collected
        if not hasattr(self.canvas, "images"):
            self.canvas.images = []
        self.canvas.images.append(photo)

class Div(Tag):
    tag_type = "Div"
    def __init__(self, children: list = [], classes: list = [], id: str = "", style: Style = Style()):
        super().__init__(children, classes, id, style)

    def _set_tag_attributes(self):
        return

class Link(Tag):
    tag_type = "Link"
    def __init__(self, href, rel, stk):
        super().__init__()
        self.href = href
        self.stk = stk

        if rel == "stylesheet":
            self.stylesheet()

    def stylesheet(self):
        spec = importlib.util.spec_from_file_location("loaded_style", self.href)
        module = importlib.util.module_from_spec(spec)
        sys.modules["loaded_style"] = module
        spec.loader.exec_module(module)
        if hasattr(module, 'style') and callable(module.style):
            module.style(self.stk)
        else:
            raise AttributeError(f"The module does not have a callable 'style' function.")

    def _set_tag_attributes(self):
        return

class Script(Tag):
    tag_type = "Script"
    def __init__(self, path, stk):
        super().__init__()
        self.path = path
        self.stk = stk

    def _load_script(self):
        spec = importlib.util.spec_from_file_location("loaded_script", self.path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["loaded_script"] = module
        spec.loader.exec_module(module)
        if hasattr(module, 'script') and callable(module.script):
            module.script(self.stk)
        else:
            raise AttributeError(f"The module does not have a callable 'script' function.")

    def _set_tag_attributes(self):
        return

screen_width = ctypes.windll.user32.GetSystemMetrics(0)
screen_height = ctypes.windll.user32.GetSystemMetrics(1)
