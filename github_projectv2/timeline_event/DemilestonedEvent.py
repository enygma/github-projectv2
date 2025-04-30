from github_projectv2.base import Base
from github_projectv2.user import User


class DemilestonedEvent(Base):
    def __init__(self, node=None):
        """Initialize the DemilestonedEvent object"""

        super().__init__(node)

        # Initialize the variables
        self.id = None
        self.actor = None
        self.createdAt = None
        self.milestoneTitle = None
        self.subject = None

        if node is not None:
            self.load(node)

    def load(self, node):
        # print(node)

        """Load the timeline item data"""
        self.id = node.get("id")
        self.createdAt = node.get("createdAt")
        self.milestoneTitle = node.get("title")
        self.subject = node.get("subject")

        self.load_actor(node.get("actor"))

    def load_actor(self, actor):
        """Load the author data"""
        type = actor.get("__typename")
        if type == "User":
            self.author = User(actor)
        else:
            self.author = None
