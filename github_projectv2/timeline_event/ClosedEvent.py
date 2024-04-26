from github_projectv2.base import Base
from github_projectv2.label import Label
from github_projectv2.user import User


class ClosedEvent(Base):
    def __init__(self, node=None):
        """Initialize the ClosedEvent object"""

        super().__init__()

        # Initialize the variables
        self.id = None
        self.actor = None
        self.closable = None
        self.closer = None
        self.reason = None
        self.url = None

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.load_actor(node.get("actor"))
        self.closable = node.get("closable")
        self.closer = node.get("closer")
        self.reason = node.get("reason")
        self.url = node.get("url")

    def load_actor(self, author):
        """Load the author data"""
        type = author.get("__typename")
        if type == "User":
            self.actor = User(author)
        else:
            self.actor = None
