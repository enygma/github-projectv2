from github_projectv2.base import Base
from github_projectv2.user import User


class AssignedEvent(Base):
    def __init__(self, node=None):
        """Initialize the AssignedEvent object"""

        super().__init__(node)

        # Initialize the variables
        self.id = None
        self.actor = None
        self.assignees = []
        self.createdAt = None
        self.updatedAt = None

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.createdAt = node.get("createdAt")
        self.updatedAt = node.get("updatedAt")

        self.load_actor(node.get("actor"))
        self.load_assignees(node.get("assignable"))

    def load_actor(self, actor):
        """Load the author data"""
        type = actor.get("__typename")
        if type == "User":
            self.actor = User(actor)
        else:
            self.actor = None

    def load_assignees(self, assignees):
        """Load the assignee data"""
        type = assignees.get("__typename")

        for assignee in assignees.get("assignees").get("nodes"):
            self.assignees.append(User(assignee))
