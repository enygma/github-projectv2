from github_projectv2.base import Base
from github_projectv2.label import Label
from github_projectv2.user import User


class CommentDeletedEvent(Base):
    def __init__(self, node=None):
        """Initialize the CommentDeletedEvent object"""

        super().__init__()

        # Initialize the variables
        self.id = None
        self.actor = None
        self.createdAt = None
        self.deletedCommentAuthor = None

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the timeline item data"""
        self.id = node.get("id")
        self.createdAt = node.get("createdAt")

        self.load_actor(node.get("actor"))
        self.load_deletedCommentAuthor(node.get("deletedCommentAuthor"))

    def load_actor(self, author):
        """Load the author data"""
        type = author.get("__typename")
        if type == "User":
            self.actor = User(author)
        else:
            self.actor = None

    def load_deletedCommentAuthor(self, author):
        """Load the deleted comment author data"""
        type = author.get("__typename")
        if type == "User":
            self.deletedCommentAuthor = User(author)
        else:
            self.deletedCommentAuthor = None
