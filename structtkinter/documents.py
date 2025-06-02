# Licensed under the MIT License

class Document():
    def __init__(self):
        self.elements = []
        self.ids = {}
        self.classes = {}

    def add_element(self, element):
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

document = Document()
