# Licensed under the MIT License

import sys
import importlib.util
import tkinter as tk
import ctypes

class Style:
    def __init__(self, name: str = None, background_color: str = None, border_bottom_left_radius: int = None, border_bottom_right_radius: int = None, border_radius: int = None, border_top_left_radius: int = None, border_top_right_radius: int = None, height: int = None, width: int = None):
        if isinstance(name, str):
            self.name = name.lower()
        else:
            self.name = name

        self.background_color = background_color

        self.border_bottom_left_radius = border_bottom_left_radius if border_bottom_left_radius != None else border_radius
        self.border_bottom_right_radius = border_bottom_right_radius if border_bottom_right_radius != None else border_radius
        self.border_top_left_radius = border_top_left_radius if border_top_left_radius != None else border_radius
        self.border_top_right_radius = border_top_right_radius if border_top_right_radius != None else border_radius

        self.height = height
        self.width = width

        if name != None and name != "":
            global styles
            styles[self.name] = self

    def __add__(self, other):
        if not isinstance(other, Style):
            raise TypeError("Can only add another Style instance")

        new_style = Style()

        new_style.background_color = self.background_color if self.background_color != None else other.background_color

        new_style.border_bottom_left_radius = self.border_bottom_left_radius if self.border_bottom_left_radius != None else other.border_bottom_left_radius
        new_style.border_bottom_right_radius = self.border_bottom_right_radius if self.border_bottom_right_radius != None else other.border_bottom_right_radius
        new_style.border_top_left_radius = self.border_top_left_radius if self.border_top_left_radius != None else other.border_top_left_radius
        new_style.border_top_right_radius = self.border_top_right_radius if self.border_top_right_radius != None else other.border_top_right_radius

        new_style.height = self.height if self.height != None else other.height
        new_style.width = self.width if self.width != None else other.width

        return new_style

class Tag:
    tag_type = "Tag"
    def __init__(self, children: list = [], classes: list = [], id: str = "", style: Style = Style()):
        if not isinstance(children, list):
            raise TypeError("children must be a list")
        if not all(isinstance(child, Tag) or isinstance(child, StyleSheet) or isinstance(child, Script) for child in children):
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

        self.height = self.style.height if self.style.height != None else 80
        self.width = self.style.width if self.style.width != None else 80

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

        global document
        document.add_element(self)

        return draw_command

    def _execute_children(self, x, y):
        draw_commands = []
        for child in self.children:
            if isinstance(child, Tag):
                child.parent = self
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

    def _set_attributes(self):
        self.background_color = self.style.background_color if self.style.background_color != None else "white"

        self.border_bottom_left_radius = self.style.border_bottom_left_radius if self.style.border_bottom_left_radius != None else 0
        self.border_bottom_right_radius = self.style.border_bottom_right_radius if self.style.border_bottom_right_radius != None else 0
        self.border_top_left_radius = self.style.border_top_left_radius if self.style.border_top_left_radius != None else 0
        self.border_top_right_radius = self.style.border_top_right_radius if self.style.border_top_right_radius != None else 0

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
            if isinstance(child, Tag):
                child.parent = self
                draw_commands = child._execute_children(x=0, y=y)
                self.draw_commands.append(child._place(x=0, y=y))
                self.draw_commands.extend(draw_commands)
                y += child._get_value("height")
            elif isinstance(child, Script):
                child._load_script()

    def __draw_box(self, x1, y1, x2, y2, r1, r2, r3, r4, fill, tag = None):
        if fill != "transparent":
            rt = max(r1, r2) # radius top
            rl = max(r2, r3) # radius left
            rb = max(r3, r4) # radius bottom
            rr = max(r4, r1) # radius right

            # center bars
            for (xs, ys), (xe, ye) in [
                ((x2-rr, y1+r1), (x2,    y2-r4)),
                ((x1+r2, y1   ), (x2-r1, y1+rt)),
                ((x1   , y1+r2), (x1+rl, y2-r3)),
                ((x1+r3, y2-rb), (x2-r4, y2   )),
                ((x1+rl, y1+rt), (x2-rr, y2-rb))
            ]:
                self.canvas.create_rectangle(
                    xs, ys, xe, ye,
                    fill=fill, outline=fill, width=0, tags=tag
                )

            # corner arcs
            for start, (xa, ya), r in [
                ( 90, (x1,      y1     ), r2),
                (  0, (x2-2*r1, y1     ), r1),
                (270, (x2-2*r4, y2-2*r4), r4),
                (180, (x1,      y2-2*r3), r3),
            ]:
                self.canvas.create_arc(
                    xa, ya, xa+2*r - 1, ya+2*r - 1,
                    start=start, extent=90, style="pieslice",
                    fill=fill, outline="", width=0,
                    tags=tag
                )

class Div(Tag):
    tag_type = "Div"
    def __init__(self, children: list = [], classes: list = [], id: str = "", style: Style = Style()):
        super().__init__(children, classes, id, style)

    def _set_attributes(self):
        self.background_color = self.style.background_color if self.style.background_color != None else "transparent"

        self.border_bottom_left_radius = self.style.border_bottom_left_radius if self.style.border_bottom_left_radius != None else 0
        self.border_bottom_right_radius = self.style.border_bottom_right_radius if self.style.border_bottom_right_radius != None else 0
        self.border_top_left_radius = self.style.border_top_left_radius if self.style.border_top_left_radius != None else 0
        self.border_top_right_radius = self.style.border_top_right_radius if self.style.border_top_right_radius != None else 0

        self.height = self.style.height if self.style.height != None else "fit-content"
        self.width = self.style.width if self.style.width != None else "100%"

class StyleSheet():
    def __init__(self, path, stk):
        spec = importlib.util.spec_from_file_location("loaded_style", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["loaded_style"] = module
        spec.loader.exec_module(module)
        if hasattr(module, 'style') and callable(module.style):
            return module.style(stk)
        else:
            raise AttributeError(f"The module does not have a callable 'style' function.")

    def __repr__(self):
        return "StyleSheet()"

class Script():
    def __init__(self, path, stk):
        self.path = path
        self.stk = stk

    def _load_script(self):
        spec = importlib.util.spec_from_file_location("loaded_script", self.path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["loaded_script"] = module
        spec.loader.exec_module(module)
        if hasattr(module, 'script') and callable(module.script):
            return module.script(self.stk)
        else:
            raise AttributeError(f"The module does not have a callable 'script' function.")

    def __repr__(self):
        return "Script()"

class Document():
    def __init__(self):
        self.elements = []
        self.ids = {}
        self.classes = {}

    def add_element(self, element: Tag):
        self.elements.append(element)
        if element.id:
            self.ids[element.id] = element
        for class_name in element.classes:
            if class_name not in self.classes:
                self.classes[class_name] = []
            self.classes[class_name].append(element)

    def get_element_by_id(self, id):
        return self.ids[id]

    def get_elements_by_class_name(self, class_name):
        return self.classes[class_name]

screen_width = ctypes.windll.user32.GetSystemMetrics(0)
screen_height = ctypes.windll.user32.GetSystemMetrics(1)
document = Document()
styles = {}