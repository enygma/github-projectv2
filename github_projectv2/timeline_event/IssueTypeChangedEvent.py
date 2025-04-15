from github_projectv2.base import Base
from github_projectv2.user import User


class IssueTypeChangedEvent(Base):
    def __init__(self, node=None):
        """Initialize the IssueTypeChangedEvent object"""

        super().__init__(node)

        # Initialize the variables
        self.id = None
        self.actor = None
        self.issueType = None
        self.createdAt = None
        self.prevIssueType = None

        if node is not None:
            self.load(node)

    def load(self, node):
        from github_projectv2.item import Item
        from github_projectv2.repository import Repository

        """Load the timeline item data"""
        self.id = node.get("id")
        self.issueType = node.get("issueType")
        self.createdAt = node.get("createdAt")
        self.prevIssueType = node.get("prevIssueType")

        self.load_actor(node.get("actor"))

    def load_actor(self, actor):
        """Load the actor data"""
        type = actor.get("__typename")
        if type == "User":
            self.actor = User(actor)
        else:
            self.actor = None
