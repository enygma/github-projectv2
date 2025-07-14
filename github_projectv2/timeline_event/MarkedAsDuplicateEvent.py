from github_projectv2.base import Base
from github_projectv2.user import User


class MarkedAsDuplicateEvent(Base):
    def __init__(self, node=None):
        """Initialize the MarkedAsDuplicateEvent object"""

        super().__init__(node)

        # Initialize the variables
        self.id = None
        self.actor = None
        self.createdAt = None
        self.canonical = None
        self.duplicate = None

        if node is not None:
            self.load(node)

    def load(self, node):
        # print(node)

        """Load the timeline item data"""
        self.id = node.get("id")
        self.createdAt = node.get("createdAt")
        self.canonical = node.get("canonical")
        self.duplicate = node.get("duplicate")

        self.load_actor(node.get("actor"))

    def load_actor(self, actor):
        """Load the author data"""
        type = actor.get("__typename")
        if type == "User":
            self.author = User(actor)
        else:
            self.author = None
