from github_projectv2.base import Base
from github_projectv2.user import User


class SubIssueAddedEvent(Base):
    def __init__(self, node=None):
        """Initialize the SubIssueAddedEvent object"""

        super().__init__()

        # Initialize the variables
        self.id = None
        self.actor = None
        self.subissue = {}
        self.createdAt = None

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.subissue = node.get("subissue")
        self.createdAt = node.get("createdAt")
        self.load_actor(node.get("actor"))

    def load_actor(self, author):
        """Load the author data"""
        type = author.get("__typename")
        if type == "User":
            self.actor = User(author)
        else:
            self.actor = None
