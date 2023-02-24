from github_projectv2.base import Base
from github_projectv2.repository import Repository


class Organization(Base):

    id = None
    name = ""
    login = ""
    description = ""
    createdAt = ""
    location = ""
    url = ""
    repositories = []

    def __init__(self, node=None):
        super().__init__()

        if node is not None:
            self.load(node)

    def load(self, node):
        self.id = node.get("id")
        self.name = node.get("name")
        self.login = node.get("login")
        self.description = node.get("description")
        self.createdAt = node.get("createdAt")
        self.location = node.get("location")
        self.url = node.get("url")

        if node.get("repositories"):
            self.repositories = node.get("repositories")

    def get(self, login):
        query = """
        {
        organization(login: "%s") {
            id
            name
            login
            description
            createdAt
            location
            url
        }
        }
        """ % (
            login
        )
        results = self.run_query(query)
        organization = results["data"]["organization"]

        # Load into this object
        self.load(organization)

        return self

    def get_repositories(self, login=None):
        if login is None:
            if self.login == "":
                raise Exception(
                    'Login is required, call "get" to load the organization first.'
                )

            login = self.login

        query = """
        {
        organization(login: "%s") {
            id
            repositories(first: 100) {
            nodes {
                id
                name
                description
                isPrivate
                isArchived
                isDisabled
                isFork
                isLocked
                isMirror
                isTemplate
            }
            pageInfo {
                hasNextPage
                endCursor
            }
            }
        }
        }
        """ % (
            login
        )
        results = self.run_query(query)
        repositories = results["data"]["organization"]["repositories"]["nodes"]

        # Load into this object
        repositoryList = []
        for repository in repositories:
            r = Repository(repository)
            repositoryList.append(r)
            self.repositories.append(r)

        return repositories
