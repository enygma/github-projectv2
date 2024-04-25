from github_projectv2.base import Base
from github_projectv2.label import Label
from github_projectv2.milestone import Milestone


class Repository(Base):
    def __init__(self, node=None):
        super().__init__()

        self.id = None
        self.name = ""
        self.description = ""
        self.isPrivate = False
        self.isArchived = False
        self.isDisabled = False
        self.isFork = False
        self.isLocked = False
        self.isMirror = False
        self.isTemplate = False
        self.org = ""
        self.milestones = []
        self.labels = []
        self.organization = ""

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
        self.labels = node.get("labels")
        self.org = node.get("org")
        self.repo = node.get("repo")
        self.organization = node.get("organization")

        if node.get("milestones"):
            self.milestones = node.get("milestones")

    def get(self, org, repo):
        self.org = org
        self.repo = repo

        template = self.jinja.get_template("partial/repository.graphql")
        repository_query = template.render({"options": {}})

        query = """
        {
        organization(login: "%s") {
            id
            repository(name: "%s") {
                %s
            }
        }
        }
        """ % (
            org,
            repo,
            repository_query,
        )
        results = self.run_query(query)
        repository = results["data"]["organization"]["repository"]

        # Set the labels
        labels = []
        for label in repository.get("labels").get("nodes"):
            labels.append(Label(label))
        repository["labels"] = labels

        # Load into this object
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
