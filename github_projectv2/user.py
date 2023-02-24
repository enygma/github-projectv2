from github_projectv2.base import Base


class User(Base):

    id = ""
    email = ""
    login = ""
    name = ""

    def __init__(self, node=None):
        super().__init__()

        if node is not None:
            self.load(node)

    def load(self, node):
        self.id = node.get("id")
        self.email = node.get("email")
        self.login = node.get("login")
        self.name = node.get("name")

    def get(self, username):
        query = """
        {
        user(login: "%s") {
            id
            email
            name
            login
        }
        }
        """ % (
            username
        )
        results = self.run_query(query)
        user = results["data"]["user"]
        self.load(user)

        return self
