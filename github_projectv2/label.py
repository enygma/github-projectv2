from github_projectv2.base import Base


class Label(Base):
    def __init__(self, node=None):
        super().__init__()

        self.id = None
        self.name = ""
        self.description = ""
        self.url = ""
        self.color = ""

        if node is not None:
            self.load(node)

    def load(self, node):
        self.id = node.get("id")
        self.name = node.get("name")
        self.description = node.get("description")
        self.url = node.get("url")
        self.color = node.get("color")
