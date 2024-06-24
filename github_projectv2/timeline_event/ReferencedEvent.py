from github_projectv2.base import Base
from github_projectv2.user import User


class ReferencedEvent(Base):
    def __init__(self, node=None):
        """Initialize the ReferencedEvent object"""

        super().__init__()

        # Initialize the variables
        self.id = None
        self.actor = None
        self.createdAt = None
        self.commit = {}
        self.commitRepository = {}
        self.isCrossRepository = False
        self.isDirectReference = False
        self.subject = {}

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.load_actor(node.get("actor"))
        self.createdAt = node.get("createdAt")
        self.isCrossRepository = node.get("isCrossRepository")
        self.isDirectReference = node.get("isDirectReference")
        self.commit = node.get("commit")
        self.commitRepository = node.get("commitRepository")
        self.subject = node.get("subject")

    def load_actor(self, author):
        """Load the author data"""
        type = author.get("__typename")
        if type == "User":
            self.actor = User(author)
        else:
            self.actor = None
