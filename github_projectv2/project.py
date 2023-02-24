import json

from github_projectv2.base import Base
from github_projectv2.field import Field
from github_projectv2.item import Item


class Project(Base):

    title = ""
    description = ""
    id = None
    number = None
    fields = []
    items = []
    org = None
    createdAt = None
    closedAt = None
    closed = False
    shortDescription = ""
    public = False
    readme = ""
    url = ""

    def __init__(self, node=None):
        super().__init__()

        if node is not None:
            self.load(node)

    def load(self, node):
        # Load into this object
        self.title = node.get("title")
        self.description = node.get("description")
        self.id = node.get("id")
        self.number = node.get("number")
        self.createdAt = node.get("createdAt")
        self.closedAt = node.get("closedAt")
        self.closed = node.get("closed")
        self.shortDescription = node.get("shortDescription")
        self.public = node.get("public")
        self.readme = node.get("readme")
        self.url = node.get("url")

        if node.get("fields") is not None:
            for field in node.get("fields"):
                self.fields.append(Field(field))

    def get(self, org: str, projectNumber: str):
        """Fetch the project data"""

        query = """
        {
        organization(login: "%s") {
            id
            projectV2(number: %s) {
                id
                title
                number
                createdAt
                closedAt
                closed
                shortDescription
                public
                readme
                url
            }
        }
        }
        """ % (
            org,
            projectNumber,
        )
        results = self.run_query(query)
        project = results["data"]["organization"]["projectV2"]

        self.org = org
        self.load(project)
        self.fields = self.get_fields(org)

        return self

    def get_fields(self, org=None):
        """Get the fields for this project"""

        if self.org is None and org is None:
            raise Exception("Organization not set")

        if org is None:
            org = self.org

        if self.number is None:
            raise Exception("Project number not set")

        query = """
        {
        organization(login: "%s") {
            id
            projectV2(number: %s) {
            id
            fields(first: 100) {
                edges {
                node {
                    ... on ProjectV2Field {
                    id
                    name
                    dataType
                    }
                    ... on ProjectV2IterationField {
                    id
                    name
                    dataType
                    }
                    ... on ProjectV2SingleSelectField {
                    id
                    name
                    dataType
                    options {
                        name
                        id
                    }
                    }
                }
                }
            }
            }
        }
        }
        """ % (
            org,
            self.number,
        )
        results = self.run_query(query)

        fields = results["data"]["organization"]["projectV2"]["fields"]["edges"]
        returnFields = []
        for field in fields:
            node = Field(field["node"])
            self.fields.append(node)
            returnFields.append(node)

        return returnFields

    def get_items(self, org=None):
        if org is None and self.org is None:
            raise Exception("Organization not set")

        if self.number is None:
            raise Exception("Project number not set")

        if org is None:
            org = self.org

        # Get the partial for the issue query
        itemQuery = self.get_query("partial/item")

        query = """
        {
        organization(login: "%s") {
            id
            projectV2(number: %s) {
            id
            items(first: 100) {
                nodes {
                id
                type
                createdAt
                }
                edges {
                node {
                    content {
                    ... on Issue {
                        %s
                    }
                    }
                }
                }
            }
            }
        }
        }
        """ % (
            org,
            self.number,
            itemQuery,
        )
        results = self.run_query(query)

        items = results["data"]["organization"]["projectV2"]["items"]["edges"]
        returnItems = []
        for index in range(len(items)):
            item = items[index]["node"]["content"]

            # Add the "nodes" ID to the item to xref the project and item
            item["projectNodeId"] = results["data"]["organization"]["projectV2"][
                "items"
            ]["nodes"][index]["id"]

            node = Item(item)
            self.items.append(node)
            returnItems.append(node)

        return returnItems

    def create(self, data):
        query = """
        mutation ($input:CreateProjectV2Input!){
            createProjectV2(input: $input) {
                clientMutationId
                projectV2 {
                    id
                    number
                    title
                }
            }
        }
        """
        results = self.run_query(query, {"input": data})
        self.load(results["data"]["createProjectV2"]["projectV2"])

        return self

    def remove_item(self, item):
        if self.id is None:
            raise Exception("Project ID not set. Call `get` to load the project first.")

        query = """
        mutation ($input:DeleteProjectV2ItemInput!){
            deleteProjectV2Item(input: $input) {
                clientMutationId
                deletedItemId
            }
        }
        """
        results = self.run_query(
            query, {"input": {"itemId": item.projectNodeId, "projectId": self.id}}
        )

        return results["data"]["deleteProjectV2Item"]["deletedItemId"]

    def add_item(self, item):
        if self.id is None:
            raise Exception("Project ID not set. Call `get` to load the project first.")

        query = """
        mutation ($input:AddProjectV2ItemByIdInput!){
            addProjectV2ItemById(input: $input) {
                clientMutationId
                item {
                    id
                }
            }
        }
        """
        results = self.run_query(
            query, {"input": {"contentId": item.id, "projectId": self.id}}
        )

        return results["data"]["addProjectV2ItemById"]["item"]["id"]

    def save(self):
        if self.id is None:
            raise Exception("Project ID not set. Call `get` to load the project first.")

        data = {
            "projectId": self.id,
            "title": self.title,
            "shortDescription": self.description,
            # Not allowing the visibility to be changed for now as it relies on a different org-level setting
            # 'public': self.public,
            "readme": self.readme,
            "closed": self.closed,
        }

        query = """
        mutation ($input:UpdateProjectV2Input!){
            updateProjectV2(input: $input) {
                clientMutationId
                projectV2 {
                    id
                }
            }
        }
        """
        results = self.run_query(query, {"input": data})

        return self
