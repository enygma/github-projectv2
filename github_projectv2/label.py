from github_projectv2.base import Base


class Label(Base):

    id = ""
    name = ""
    description = ""

    def __init__(self, node=None):
        super().__init__()

        if node is not None:
            self.load(node)

    def load(self, node):
        self.id = node.get("id")
        self.name = node.get("name")
        self.description = node.get("description")
