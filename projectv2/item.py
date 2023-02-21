from projectv2.base import Base
from projectv2.label import Label
from projectv2.user import User


class Item(Base):
    def __init__(self, node=None):
        """Initialize the item object"""

        super().__init__()

        # Initialize the variables
        self.id = None
        self.type = ""
        self.created = ""
        self.assignees = []
        self.title = ""
        self.number = ""
        self.updatedAt = ""
        self.url = ""
        self.body = ""
        self.closed = False
        self.closedAt = ""
        self.author = []
        self.labels = []
        self.projectNodeId = None
        self.trackedIssues = []
        self.trackedInIssues = []

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the item data"""

        self.id = node.get("id")
        self.type = "ISSUE"
        self.created = node.get("createdAt")
        self.title = node.get("title")
        self.number = node.get("number")
        self.updatedAt = node.get("updatedAt")
        self.url = node.get("url")
        self.body = node.get("body")
        self.closed = node.get("closed")
        self.closedAt = node.get("closedAt")
        self.projectNodeId = node.get("projectNodeId")
        self.author = User(node.get("author"))

        # Make sure the tracking issues are loaded correctly
        if node.get("trackedIssues") is not None:
            self.load_tracked_issues(node)

        # Make sure the tracked issues are loaded correctly
        if node.get("trackedInIssues") is not None:
            self.load_tracked_in_issues(node)

        # Make sure our assignees are loaded correctly
        if node.get("assignees") is not None:
            self.load_assignees(node)

    def load_assignees(self, node):
        """Load the assignees"""

        if node.get("assignees").get("edges") is None:
            return

        assignees = node.get("assignees").get("edges")
        for assignee in assignees:
            self.assignees.append(User(assignee.get("node")))

    def load_tracked_issues(self, node):
        """Load the tracked issues"""

        if node.get("trackedIssues") is None:
            return

        trackedIssues = node.get("trackedIssues").get("edges")
        for item in trackedIssues:
            self.trackedIssues.append(Item(item.get("node")))

    def load_tracked_in_issues(self, node):
        """Load the tracked in issues"""

        if node.get("trackedInIssues") is None:
            return

        trackedInIssues = node.get("trackedInIssues").get("edges")
        for item in trackedInIssues:
            self.trackedInIssues.append(Item(item.get("node")))

    ## ----------------------------------------

    def get(self, org: str, repo: str, itemId: str):
        """Get the item data"""

        # Get the partial query for an Item
        itemQuery = self.get_query("partial/item")
        query = """
        {
        organization(login: "%s") {
            id
            repository(name: "%s") {
            id
            issue(number: %s) {
                %s
            }
            }
        }
        }
        """ % (
            org,
            repo,
            itemId,
            itemQuery,
        )
        results = self.run_query(query)

        item = results.get("data").get("organization").get("repository").get("issue")
        # Set the base values
        self.load(item)

        # Set the assignees
        self.load_assignees(item)

        # Set the author
        self.author = User(item.get("author"))

        # Set the labels
        for label in item.get("labels").get("edges"):
            self.labels.append(Label(label.get("node")))

    def update_field_value(self, project, field, option):
        """
        Update the field value

        :param project: The Project object
        :param field: The Field object
        :param option: The Option object
        """

        query = """
        mutation {
            updateProjectV2ItemFieldValue(input: {itemId: "%s", fieldId: "%s", value: {singleSelectOptionId:"%s"}, projectId:"%s"}) {
                clientMutationId
            }
        }
        """ % (
            self.projectNodeId,
            field.id,
            option.id,
            project.id,
        )
        results = self.run_query(query)

        return results

    def clear_field_value(self, project, field):
        """
        Clear the field value

        :param project: The Project object
        :param field: The Field object
        """

        fieldId = field.id
        projectId = project.id

        query = """
        mutation {
            clearProjectV2ItemFieldValue(input: {itemId: "%s", fieldId: "%s", projectId:"%s"}) {
                clientMutationId,
                projectV2Item {
                    id
                }
            }
        }""" % (
            self.projectNodeId,
            fieldId,
            projectId,
        )
        results = self.run_query(query)

        return results

    def create(self, repository, data):
        """
        Create a new issue

        :param repository: The Repository object
        :param data: The data (dict) to create the issue with

        example_data = {
            'assigneeIds': ['MDQ6VXNlcjE='],
            'body': 'This is the body',
            'issueTemplate': 'MDU6SXNzdWUxMjM=',
            'milestoneId': 'MDk6TWlsZXN0b25lMjM=',
            'title': 'This is the title'
        }
        """

        if data.get("assigneeIds") is not None:
            assigneeIds = self.convert_quotes(data.get("assigneeIds"))

        query = """
        mutation {
            createIssue(input: {assigneeIds: %s, body: "%s",%s labelIds: %s, %s, repositoryId: "%s", title: "%s"}) {
                clientMutationId,
                issue {
                    %s
                }
            }
        }""" % (
            assigneeIds,
            data.get("body"),
            'issueTemplate: "%s",' % data.get("issueTemplate")
            if data.get("issueTemplate")
            else "",
            data.get("labelIds") if data.get("labelIds") else "[]",
            'milestoneId: "%s",' % data.get("milestoneId")
            if data.get("milestoneId")
            else "",
            repository.id,
            data.get("title"),
            self.get_query("partial/item"),
        )

        results = self.run_query(query)

        item = Item(results.get("data").get("createIssue").get("issue"))
        return item

    def close(self):
        """Close the issue"""

        if self.id is None:
            raise Exception("No ID set")

        query = """
        mutation {
            closeIssue(input: {issueId: "%s"}) {
                clientMutationId
            }
        }
        """ % (
            self.id
        )
        results = self.run_query(query)

        return results
