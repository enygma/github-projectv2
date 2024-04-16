from github_projectv2.base import Base
from github_projectv2.user import User


class SubscribedEvent(Base):
    def __init__(self, node=None):
        """Initialize the SubscribedEvent object"""

        super().__init__(node)

        # Initialize the variables
        self.id = None
        self.actor = None
        self.createdAt = None
        self.subscribable = None

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.createdAt = node.get("createdAt")
        self.subscribable = node.get("subscribable")

        self.load_actor(node.get("actor"))

    def load_actor(self, actor):
        """Load the author data"""
        type = actor.get("__typename")
        if type == "User":
            self.actor = User(actor)
        else:
            self.actor = None
