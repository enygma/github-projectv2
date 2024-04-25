from github_projectv2.base import Base


class Milestone(Base):

    description = ""
    id = None
    number = None
    title = ""
    state = ""
    dueOn = ""

    def __init__(self, node=None):
        super().__init__()

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the milestone data into this object"""

        self.id = node.get("id")
        self.description = node.get("description")
        self.number = node.get("number")
        self.title = node.get("title")
        self.state = node.get("state")
        self.dueOn = node.get("dueOn")

    def get(self, org: str, repo: str, number: str):
        """Fetch the milestone data"""

        milestonePartial = self.get_query("partial/milestone")

        query = """
        {
        organization(login: "%s") {
            id
            repository(name: "%s") {
            id
            milestone(number: %s) {
                %s
            }
            }
        }
        }
        """ % (
            org,
            repo,
            number,
            milestonePartial,
        )
        results = self.run_query(query)
        milestone = results["data"]["organization"]["repository"]["milestone"]

        # Load into this object
        self.load(milestone)

        return self
