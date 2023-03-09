from github_projectv2.base import Base


class View(Base):

    id = ""
    name = ""
    layout = ""
    sortBy = {"field": {"name": "", "id": "", "dataType": ""}, "direction": ""}
    groupBy = {"id": "", "name": ""}
    number = ""

    def __init__(self, node=None):
        super().__init__()

        if node is not None:
            self.load(node)

    def load(self, node):
        self.id = node.get("id")
        self.name = node.get("name")
        self.layout = node.get("layout")
        self.number = node.get("number")

        if node.get("sortBy") is not None:
            self.load_sortby(node.get("sortBy"))

        if node.get("groupBy") is not None:
            self.load_groupby(node.get("groupBy"))

    def load_sortby(self, node):
        if len(node["edges"]) == 0:
            return

        node = node["edges"][0]["node"]

        self.sortBy["field"]["name"] = node["field"]["name"]
        self.sortBy["field"]["id"] = node["field"]["id"]
        self.sortBy["field"]["dataType"] = node["field"]["dataType"]
        self.sortBy["direction"] = node["direction"]

    def load_groupby(self, node):
        if len(node["edges"]) == 0:
            return

        node = node["edges"][0]["node"]
        self.groupBy["id"] = node["id"]
        self.groupBy["name"] = node["name"]
