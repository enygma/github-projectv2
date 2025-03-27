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
        self.timelineItems = []
        self.organization = ""
        self.repository = None
        self.projectItems = []
        self.repo = None
        self.fields = []
        self.subissues = []
        self.template = None

        if node is not None:
            self.load(node)

    def load(self, node):
        """Load the item data"""
        # print(node)

        self.id = node.get("id")
        self.type = node.get("__typename")
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
        self.repo = node.get("repo")
        self.fields = []
        self.timelineItems = []
        self.template = None

        if node.get("subissues") is not None:
            self.organization = node.get("subissues")

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
        if node.get("timelineItems") is not None:
            self.load_timeline(node)

        if node.get("repository") is not None:
            self.repository = Repository(node.get("repository"))

        projectItems = "projectItems" if self.type == "Issue" else "projectV2Items"
        if node.get(projectItems) is not None:
            for projectItem in node.get(projectItems).get("edges"):
                # print(projectItem)
                for field in projectItem.get("node").get("fieldValues").get("edges"):
                    node = field.get("node")
                    f = Field(node.get("field"))
                    f.load_value(node)
                    f.updated = node.get("updatedAt")
                    self.fields.append(f)

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
        self.timelineItems = []

        if node.get("timelineItems") is None:
            return

        # For each of the items in the timeline, make an object and push it into the list
        timeline = node.get("timelineItems").get("edges")
        for event in timeline:
            event_type = event.get("node").get("__typename")
            evt = eval("timeline_event.%s.%s()" % (event_type, event_type))
            evt.load(event.get("node"))

            self.timelineItems.append(evt)

    def load_repository(self, node):
        """Load the repository data"""

        self.repo = Repository(node)

    def find_field_by_name(self, name):
        """Find a field by name"""

        for field in self.fields:
            if field.name == name:
                return field

        return None

    ## ----------------------------------------

    def get(self, org: str, repo: str, itemId: str):
        """Get the item data"""

        template = self.jinja.get_template("partial/issue_item.graphql")
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
        # print(results)

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

    def get_timeline(self):
        """Get the timeline data"""

        # Timeliines are only available for issues
        if self.type != "Issue":
            return []

        if self.id == "" or self.id is None:
            raise Exception("No ID set, fetch item (get) first")
        if self.organization == "" or self.organization is None:
            raise Exception("No org set, fetch item (get) first")
        if self.repository == "" or self.repository is None:
            raise Exception("No repo set, fetch item (get) first")

        template = self.jinja.get_template("partial/issue-timeline-events.graphql")
        timeline_query = template.render({"options": {}})

        query = """
        {
            organization(login: "%s") {
                id
                name
                repository(name: "%s") {
                    issue(number: %s) {
                        %s
                    }
                }
            }
        }
        """ % (
            self.organization.name,
            self.repository.name,
            self.number,
            timeline_query,
        )
        # print(query)

        results = self.run_query(query)
        timeline = (
            results.get("data")
            .get("organization")
            .get("repository")
            .get("issue")
            .get("timelineItems")
        )

        # print('TIMELINE')
        # print(self.timelineItems)

        # If they've already been loaded, reset them to an empty list
        self.timelineItems = []
        self.load_timeline(
            results.get("data").get("organization").get("repository").get("issue")
        )

        return timeline

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
        "assignees" is an optional value, a set of usernames. If provided it will be translated into assigneeIds
        "labels" is an optional value, a set of label strings. If provided it will be translated into labelIds
        """

        # If the repository value is a string, then we need to create a new Repository object
        if isinstance(repository, str):
            repository = Repository()
            repository.get(repository)

        # Check to see if the "assignees" value is set and make sure the assigneeIds isn't. AssigneeIds overwrites "assignees" If so translate them into IDs.
        assigneeIds = []
        if data.get("assigneesId") is None and data.get("assignees") is not None:
            # MAek sure the assignees are a list
            if not isinstance(data.get("assignees"), list):
                raise Exception("Assignees must be a list")

            for assignee in data.get("assignees"):
                user = User()
                user.get(assignee)
                assigneeIds.append(user.id)

        elif data.get("assigneeIds") is not None:
            assigneeIds = data.get("assigneeIds")

        # If the "labels" value is set and "labelIds" isn't, translate them into IDs
        labelIds = []
        if data.get("labels") is not None and data.get("labelIds") is None:
            if not isinstance(data.get("labels"), list):
                raise Exception("Labels must be a list")

            self.labels = repository.get_labels()
            for label in self.labels:
                if label.name in data.get("labels"):
                    labelIds.append(label.id)

        elif data.get("labelIds") is not None:
            labelIds = data.get("labelIds")

        template = self.jinja.get_template("partial/issue_item.graphql")
        item_query = template.render({"options": []})

        query = """
        mutation ($input:CreateIssueInput!) {
            createIssue(input: $input) {
                clientMutationId,
                issue {
                    %s
                }
            }
        }""" % (
            item_query,
        )

        # {assigneeIds: $assignees, body: $body,%s labelIds: $labelIds, %s repositoryId: $repositoryId, title: $title}
        input = {
            "assigneeIds": assigneeIds,
            "body": data.get("body"),
            "repositoryId": repository.id,
            "title": data.get("title"),
            "labelIds": labelIds,
        }
        if data.get("issueTemplate"):
            input["issueTemplate"] = data.get("issueTemplate")

        if data.get("milestoneId"):
            input["milestoneId"] = data.get("milestoneId")

        results = self.run_query(query, {"input": input})

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
        itemQuery = self.get_query("partial/issue_item")

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

    def assign(self, assignee):
        """Assign the issue"""

        if self.id == "" or self.id is None:
            raise Exception("No ID set, fetch item (get) first")

        query = """
        mutation {
            addAssigneesToAssignable(input: {assignableId: "%s", assigneeIds: ["%s"]}) {
                clientMutationId
            }
        }
        """ % (
            self.id,
            assignee.id,
        )
        results = self.run_query(query)
        self.assignees.append(assignee)
        return results

    def add_subissue(self, subissue):
        """Add a subissue"""

        if self.id == "" or self.id is None:
            raise Exception("No ID set, fetch item (get) first")

        if subissue.id == "" or subissue.id is None:
            raise Exception("No ID set, fetch item (get) first")

        query = """
        mutation {
            addSubIssue(input: {issueId: "%s", subIssueId: "%s"}) {
                clientMutationId
            }
        }
        """ % (
            self.id,
            subissue.id,
        )
        results = self.run_query(query)
        return results

    def get_subissues(self):
        """Get the subissues"""

        if self.id == "" or self.id is None:
            raise Exception("No ID set, fetch item (get) first")

        template = self.jinja.get_template("partial/issue_item.graphql")
        item_query = template.render({"options": {}})

        query = """
        {
            node(id: "%s") {
                ... on Issue {
                    subIssues(first: 100) {
                        edges {
                            node {
                                %s
                            }
                        }
                    }
                }
            }
        }
        """ % (
            self.id,
            item_query,
        )
        results = self.run_query(query)

        subissue_list = results["data"]["node"]["subIssues"]["edges"]
        for subissue in subissue_list:
            self.subissues.append(Item(subissue.get("node")))

        return self.subissues
