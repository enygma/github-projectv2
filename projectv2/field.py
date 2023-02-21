from projectv2.base import Base
from projectv2.option import Option


class Field(Base):

    id = None
    name = ""
    dataType = ""
    options = []

    def __init__(self, node):
        super().__init__()

        self.id = node.get("id")
        self.name = node.get("name")
        self.dataType = node.get("dataType")

        if self.dataType == "SINGLE_SELECT":
            for option in node.get("options"):
                self.options.append(Option(option))
