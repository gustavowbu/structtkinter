# Licensed under the MIT License

class Style():
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

styles = {}
