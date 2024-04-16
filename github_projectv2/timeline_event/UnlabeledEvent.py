from github_projectv2.base import Base
from github_projectv2.label import Label


class UnlabeledEvent(Base):
    def __init__(self, node=None):
        """Initialize the UnlabeledEvent object"""

        super().__init__(node)

        # Initialize the variables
        self.id = None
        self.actor = None
        self.label = None
        self.createdAt = None

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.createdAt = node.get("createdAt")
        self.label = Label(node.get("label"))
