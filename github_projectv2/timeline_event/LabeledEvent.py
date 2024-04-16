from github_projectv2.base import Base
from github_projectv2.label import Label
from github_projectv2.user import User


class LabeledEvent(Base):
    def __init__(self, node=None):
        """Initialize the LabeledEvent object"""

        super().__init__()

        # Initialize the variables
        self.id = None
        self.actor = []
        self.label = []

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.load_actor(node.get("actor"))
        self.label = Label(node.get("label"))

    def load_actor(self, author):
        """Load the author data"""
        type = author.get("__typename")
        if type == "User":
            self.actor = User(author)
        else:
            self.actor = None
