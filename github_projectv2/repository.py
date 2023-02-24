from github_projectv2.base import Base
from github_projectv2.milestone import Milestone


class Repository(Base):

    id = None
    name = ""
    description = ""
    isPrivate = False
    isArchived = False
    isDisabled = False
    isFork = False
    isLocked = False
    isMirror = False
    isTemplate = False
    org = ""
    milestones = []

    def __init__(self, node=None):
        super().__init__()

        if node is not None:
            self.load(node)

    def load(self, node):
        self.id = node.get("id")
        self.name = node.get("name")
        self.description = node.get("description")
        self.isPrivate = node.get("isPrivate")
        self.isArchived = node.get("isArchived")
        self.isDisabled = node.get("isDisabled")
        self.isFork = node.get("isFork")
        self.isLocked = node.get("isLocked")
        self.isMirror = node.get("isMirror")
        self.isTemplate = node.get("isTemplate")

        if node.get("milestones"):
            self.milestones = node.get("milestones")

    def get(self, org, repo):
        query = """
        {
        organization(login: "%s") {
            id
            repository(name: "%s") {
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
        }
        }
        """ % (
            org,
            repo,
        )
        results = self.run_query(query)
        repository = results["data"]["organization"]["repository"]

        # Load into this object
        self.org = org
        self.load(repository)

        return self

    def get_milestones(self):
        if self.org == "":
            raise Exception(
                'Organization is required, call "get" to load the repository first.'
            )

        milestonePartial = self.get_query("partial/milestone")

        query = """
        {
        organization(login: "%s") {
            id
            repository(name: "%s") {
            id
            milestones(first: 100) {
                nodes {
                %s
                }
            }
            }
        }
        }
        """ % (
            self.org,
            self.name,
            milestonePartial,
        )
        results = self.run_query(query)
        milestones = results["data"]["organization"]["repository"]["milestones"][
            "nodes"
        ]

        returnItems = []
        for milestone in milestones:
            node = Milestone(milestone)

            returnItems.append(node)
            self.milestones.append(node)

        return returnItems
