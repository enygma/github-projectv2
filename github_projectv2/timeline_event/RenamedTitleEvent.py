from github_projectv2.base import Base
from github_projectv2.user import User


class RenamedTitleEvent(Base):
    def __init__(self, node=None):
        """Initialize the RenamedTitleEvent object"""

        super().__init__()

        # Initialize the variables
        self.id = None
        self.actor = None
        self.createdAt = None
        self.currentTitle = None
        self.previousTitle = None
        self.subject = None

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.load_actor(node.get("actor"))
        self.createdAt = node.get("createdAt")
        self.currentTitle = node.get("currentTitle")
        self.previousTitle = node.get("previousTitle")
        self.subject = node.get("subject")

    def load_actor(self, author):
        """Load the author data"""
        type = author.get("__typename")
        if type == "User":
            self.actor = User(author)
        else:
            self.actor = None
