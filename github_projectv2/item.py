from github_projectv2 import timeline_event
from github_projectv2.base import Base
from github_projectv2.comment import Comment
from github_projectv2.field import Field
from github_projectv2.label import Label
from github_projectv2.option import Option
from github_projectv2.organization import Organization
from github_projectv2.repository import Repository
from github_projectv2.user import User


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
        self.comments = []
        self.timeline = []
        self.organization = ""
        self.repository = None

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
        self.organization = node.get("org")

        # Make sure the tracking issues are loaded correctly
        if node.get("trackedIssues") is not None:
            self.load_tracked_issues(node)

        # Make sure the tracked issues are loaded correctly
        if node.get("trackedInIssues") is not None:
            self.load_tracked_in_issues(node)

        # Make sure our assignees are loaded correctly
        if node.get("assignees") is not None:
            self.load_assignees(node)

        # Make sure our labels are loaded correctly
        if node.get("labels") is not None:
            self.load_labels(node)

        # Make sure our comments are loaded correctly
        if node.get("comments") is not None:
            self.load_comments(node)

        # Make sure our timeline is loaded correctly
        if node.get("timeline") is not None:
            self.load_timeline(node)

        if node.get("repository") is not None:
            self.repository = Repository(node.get("repository"))

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

    def load_labels(self, node):
        """Load the labels"""

        if node.get("labels") is None:
            return

        labels = node.get("labels").get("edges")
        for label in labels:
            self.labels.append(Label(label.get("node")))

    def load_comments(self, node):
        """Load the comments"""

        if node.get("comments") is None:
            return

        comments = node.get("comments").get("edges")
        for comment in comments:
            self.comments.append(Comment(comment.get("node")))

    def load_timeline(self, node):
        """Load the timeline"""

        if node.get("timelineItems") is None:
            return

        # For each of the items in the timeline, make an object and push it into the list
        timeline = node.get("timelineItems").get("edges")
        for event in timeline:
            event_type = event.get("node").get("__typename")
            evt = eval("timeline_event.%s.%s()" % (event_type, event_type))
            evt.load(event.get("node"))

            self.timeline.append(evt)

    def load_repository(self, node):
        """Load the repository data"""

        self.repo = Repository(node)

    ## ----------------------------------------

    def get(self, org: str, repo: str, itemId: str):
        """Get the item data"""

        template = self.jinja.get_template("partial/item.graphql")
        item_query = template.render(
            {"options": {"includeComments": True, "includeTimelineEvents": True}}
        )

        template = self.jinja.get_template("partial/repository.graphql")
        repo_query = template.render({"options": {}})

        # Get the partial query for an Item
        # itemQuery = self.get_query("partial/item")
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
            repository(name: "%s") {
                %s
                issue(number: %s) {
                    %s
                }
            }
        }
        }
        """ % (
            org,
            repo,
            repo_query,
            itemId,
            item_query,
        )
        results = self.run_query(query)
        item = results.get("data").get("organization").get("repository").get("issue")

        # Set the base values
        self.load(item)

        # Set the assignees
        self.load_assignees(item)

        # Set the timeline events
        self.load_timeline(item)

        # Set the author
        self.author = User(item.get("author"))

        # Set the labels
        for label in item.get("labels").get("edges"):
            self.labels.append(Label(label.get("node")))

        # Set the organization
        self.organization = Organization(results.get("data").get("organization"))

        # And the repository
        self.repository = Repository(
            results.get("data").get("organization").get("repository")
        )

    def update_field_value(self, project, field, input):
        """
        Update the field value

        :param project: The Project object
        :param field: The Field object
        :param value: Either an Option object if the field is a SINGLE_SELECT, or a string
        """

        match field.dataType:
            case "SINGLE_SELECT":
                if not isinstance(input, Option):
                    raise Exception(
                        'Input for "update_field_value" method must be an Option object'
                    )
                value = '{singleSelectOptionId:"%s"}' % input.id
            case "DATE":
                value = '{date:"%s"}' % input
            case "TEXT":
                value = '{text:"%s"}' % input
            case "NUMBER":
                value = "{number:%s}" % input

        query = """
        mutation {
            updateProjectV2ItemFieldValue(input: {itemId: "%s", fieldId: "%s", value: %s, projectId:"%s"}) {
                clientMutationId
            }
        }
        """ % (
            self.projectNodeId,
            field.id,
            value,
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

        # See if found is not a type of Field
        if not isinstance(field, Field):
            # Find the field
            fields = project.get_fields()
            for f in fields:
                if f.name == field:
                    field = f

        # Make sure we found the field
        if field is None:
            raise Exception("Could not find field: %s" % field)

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

    def save(self):
        """Save the issue"""

        if self.id is None:
            raise Exception("No ID set")

        data = {"id": self.id, "title": self.title, "body": self.body}
        itemQuery = self.get_query("partial/item")

        query = """
        mutation ($input:UpdateIssueInput!){
            updateIssue(input: $input) {
                clientMutationId,
                issue {
                    %s
                }
            }
        }
        """ % (
            itemQuery
        )
        results = self.run_query(query, {"input": data})
        return results

    def add_label(self, label_name):
        """Add a label"""

        from github_projectv2.repository import Repository

        if self.id == "" or self.id is None:
            raise Exception("No ID set, fetch item (get) first")
        if self.organization == "" or self.organization is None:
            raise Exception("No org set, fetch item (get) first")
        if self.repository == "" or self.repository is None:
            raise Exception("No repo set, fetch item (get) first")

        # Get the list of labels from the repository
        repo = Repository()
        repo.get(self.organization.name, self.repository.name)

        label_id = None
        for label in repo.labels:
            if label.name == label_name:
                label_id = label.id
                break

        if label_id is None:
            raise Exception("Label %s not found" % label.name)

        query = """
        mutation {
            addLabelsToLabelable(input: {labelableId: "%s", labelIds: ["%s"]}) {
                clientMutationId
            }
        }
        """ % (
            self.id,
            label_id,
        )
        results = self.run_query(query)

        return results

    def close(self, reason="COMPLETED"):
        """Close the issue"""

        if self.id == "" or self.id is None:
            raise Exception("No ID set, fetch item (get) first")

        query = """
        mutation {
            closeIssue(input: {issueId: "%s", stateReason: %s}) {
                clientMutationId
            }
        }
        """ % (
            self.id,
            reason,
        )
        results = self.run_query(query)
        return results

    def make_comment(self, content):
        """Make a comment"""

        if self.id == "" or self.id is None:
            raise Exception("No ID set, fetch item (get) first")

        query = """
        mutation {
            addComment(input: {subjectId: "%s", body: "%s"}) {
                clientMutationId
            }
        }
        """ % (
            self.id,
            content,
        )
        results = self.run_query(query)
        return results
