from github_projectv2.base import Base
from github_projectv2.option import Option


class Field(Base):

    id = None
    name = ""
    dataType = ""
    options = []
    value = None
    updated = None

    def __init__(self, node):
        super().__init__()
        self.load(node)

    def load(self, node):
        self.id = node.get("id")
        self.name = node.get("name")
        self.dataType = node.get("dataType")
        self.options = []
        self.updated = node.get("updatedAt")

        if self.dataType == "SINGLE_SELECT":
            # If we have options, load them
            for option in node.get("options"):
                self.options.append(Option(option))

    def load_value(self, node):
        if self.dataType == "SINGLE_SELECT":
            self.value = Option({"id": node.get("optionId"), "name": node.get("name")})

        if self.dataType == "TEXT":
            if node.get("text") is not None:
                self.value = node.get("text")

    def find_option(self, name):
        if self.dataType != "SINGLE_SELECT":
            raise Exception("This field is not a single select field")

        for option in self.options:
            if option.name == name:
                return option

        return None
