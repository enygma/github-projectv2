from github_projectv2.base import Base
from github_projectv2.user import User


class AddedToProjectEvent(Base):
    def __init__(self, node=None):
        """Initialize the AddedToProjectEvent object"""

        super().__init__()

        # Initialize the variables
        self.id = None
        self.actor = None
        self.createdAt = None
        self.databaseId = None
        self.project = {}
        self.projectCard = {}
        self.projectColumnName = None

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.load_actor(node.get("actor"))
        self.createdAt = node.get("createdAt")
        self.databaseId = node.get("databaseId")
        self.project = node.get("project")
        self.projectCard = node.get("projectCard")
        self.projectColumnName = node.get("projectColumnName")

    def load_actor(self, author):
        """Load the author data"""
        type = author.get("__typename")
        if type == "User":
            self.actor = User(author)
        else:
            self.actor = None
