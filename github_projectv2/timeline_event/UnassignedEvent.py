from github_projectv2.base import Base
from github_projectv2.user import User


class UnassignedEvent(Base):
    def __init__(self, node=None):
        """Initialize the UnassignedEvent object"""

        super().__init__(node)

        # Initialize the variables
        self.id = None
        self.actor = None
        self.assignable = None
        self.createdAt = None
        self.assignees = []

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")

        self.load_actor(node.get("actor"))
        self.load_assignees(node.get("assignable"))

    def load_actor(self, actor):
        """Load the author data"""
        type = actor.get("__typename")
        if type == "User":
            self.author = User(actor)
        else:
            self.author = None

    def load_assignees(self, assignees):
        """Load the assignee data"""
        type = assignees.get("__typename")

        for assignee in assignees.get("assignees").get("nodes"):
            self.assignees.append(User(assignee))
