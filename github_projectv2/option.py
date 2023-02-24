from github_projectv2.base import Base


class Option(Base):

    id = None
    name = ""

    def __init__(self, node):
        super().__init__()

        self.id = node.get("id")
        self.name = node.get("name")
