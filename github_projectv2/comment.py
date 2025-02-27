from github_projectv2.base import Base
from github_projectv2.user import User


class Comment(Base):
    def __init__(self, node=None):
        """Initialize the item object"""

        super().__init__()

        # Initialize the variables
        self.id = None
        self.body = ""
        self.created = node.get("createdAt")
        self.updatedAt = node.get("updatedAt")
        self.author = User(node.get("author"))

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the comment data"""

        self.id = node.get("id")
        self.body = node.get("body")
        self.created = node.get("createdAt")
        self.updatedAt = node.get("updatedAt")
        self.author = User(node.get("author"))

    def delete(self):
        """Delete the comment"""

        query = """
        mutation deleteComment($id: ID!) {
            deleteIssueComment(input: {id: $id}) {
                clientMutationId
            }
        }
        """
        data = {"id": self.id}
        self.run_query(query, data)
