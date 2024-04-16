from github_projectv2.base import Base
from github_projectv2.user import User


class IssueComment(Base):
    def __init__(self, node=None):
        """Initialize the IssueComment object"""

        super().__init__(node)

        # Initialize the variables
        self.id = None
        self.author = None
        self.body = None
        self.createdAt = None
        self.updatedAt = None
        self.url = None
        self.repository = None

        if node is not None:
            self.load(node)

    def load(self, node):
        from github_projectv2.item import Item
        from github_projectv2.repository import Repository

        """Load the timeline item data"""
        self.id = node.get("id")
        self.body = node.get("body")
        self.createdAt = node.get("createdAt")
        self.updatedAt = node.get("updatedAt")
        self.url = node.get("url")

        self.load_author(node.get("author"))
        self.issue = Item(node.get("issue"))
        self.repository = Repository(node.get("repository"))

    def load_author(self, author):
        """Load the author data"""
        type = author.get("__typename")
        if type == "User":
            self.author = User(author)
        else:
            self.author = None
