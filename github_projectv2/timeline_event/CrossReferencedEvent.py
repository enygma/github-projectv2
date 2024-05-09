from github_projectv2.base import Base
from github_projectv2.user import User


class CrossReferencedEvent(Base):
    def __init__(self, node=None):
        """Initialize the CrossReferencedEvent object"""

        super().__init__()

        # Initialize the variables
        self.id = None
        self.actor = None
        self.createdAt = None
        self.isCrossRepository = False
        self.referencedAt = None
        self.resourcePath = None
        self.source = None
        self.target = None
        self.willCloseTarget = False
        self.url = None

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.load_actor(node.get("actor"))
        self.createdAt = node.get("createdAt")
        self.isCrossRepository = node.get("isCrossRepository")
        self.referencedAt = node.get("referencedAt")
        self.resourcePath = node.get("resourcePath")
        self.source = node.get("source")
        self.target = node.get("target")
        self.willCloseTarget = node.get("willCloseTarget")
        self.url = node.get("url")

    def load_actor(self, author):
        """Load the author data"""
        type = author.get("__typename")
        if type == "User":
            self.actor = User(author)
        else:
            self.actor = None
