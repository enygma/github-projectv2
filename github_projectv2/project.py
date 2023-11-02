import json

from github_projectv2.base import Base
from github_projectv2.field import Field
from github_projectv2.item import Item
from github_projectv2.view import View


class Project(Base):

    title = ""
    description = ""
    id = None
    number = None
    fields = []
    items = []
    views = []
    org = None
    createdAt = None
    closedAt = None
    closed = False
    shortDescription = ""
    public = False
    readme = ""
    url = ""

    itemEndCursor = ""
    itemHasNextPage = False

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

        self.itemEndCursor = ""
        self.itemHasNextPage = False

        if node.get("fields") is not None:
            for field in node.get("fields"):
                self.fields.append(Field(field))

    def get(self, org: str, projectNumber: str):
        """Fetch the project data"""

        template = self.jinja.get_template("project/get.graphql")
        query = template.render(
            {
                "orgName": org,
                "projectNumber": projectNumber,
            }
        )
        results = self.run_query(query)

        # See if the project was found
        if results["data"]["organization"]["projectV2"] is None:
            raise Exception("ERROR: %s" % results["errors"][0]["message"])

        project = results["data"]["organization"]["projectV2"]

        self.org = org
        self.load(project)
        self.fields = self.get_fields(org=org)

        return self

    def get_fields(self, **kwargs):
        """Get the fields for this project"""

        if "org" in kwargs:
            org = kwargs["org"]
        else:
            org = None

        if "options" in kwargs:
            options = kwargs["options"]
        else:
            options = {}

        if self.org is None and org is None:
            raise Exception("Organization not set")

        if org is None:
            org = self.org

        if self.number is None:
            raise Exception("Project number not set")

        # Get the template and build the query
        template = self.jinja.get_template("project/get_fields.graphql")
        query = template.render(
            {"orgName": org, "projectNumber": self.number, "options": options}
        )
        results = self.run_query(query)

        fields = results["data"]["organization"]["projectV2"]["fields"]["edges"]
        returnFields = []
        for field in fields:
            node = Field(field["node"])
            self.fields.append(node)
            returnFields.append(node)

        return returnFields

    def get_items(self, **kwargs):

        if "org" in kwargs:
            org = kwargs["org"]
        else:
            org = None

        if "options" in kwargs:
            options = kwargs["options"]
        else:
            options = {}

        if org is None and self.org is None:
            raise Exception("Organization not set")

        if self.number is None:
            raise Exception("Project number not set")

        if org is None:
            org = self.org

        # Get the template and build the query
        template = self.jinja.get_template("project/get_items.graphql")
        query = template.render(
            {"orgName": org, "projectNumber": self.number, "options": options}
        )

        # Replace for our "AFTER" so we can paginate
        query = query.replace(
            "AFTER", '"{}"'.format(self.itemEndCursor) if self.itemEndCursor else "null"
        )
        results = self.run_query(query)

        # Get the page info to see about pagination
        pageInfo = results["data"]["organization"]["projectV2"]["items"]["pageInfo"]
        if pageInfo["hasNextPage"]:
            self.itemHasNextPage = True
            self.itemEndCursor = pageInfo["endCursor"]
        else:
            self.itemHasNextPage = False
            self.itemEndCursor = ""

        # Get the items from the results and make them into Item objects
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

    def get_views(self, **kwargs):
        if "org" in kwargs:
            org = kwargs["org"]
        else:
            org = None

        if org is None and self.org is None:
            raise Exception("Organization not set")

        if self.number is None:
            raise Exception("Project number not set")

        if org is None:
            org = self.org

        if "options" in kwargs:
            options = kwargs["options"]
        else:
            options = {}

        # Get the template and build the query
        template = self.jinja.get_template("project/get_views.graphql")
        query = template.render(
            {"orgName": org, "projectNumber": self.number, "options": options}
        )

        results = self.run_query(query)
        views = results["data"]["organization"]["projectV2"]["views"]["edges"]

        returnItems = []
        for index in range(len(views)):
            item = views[index]["node"]

            node = View(item)
            self.views.append(node)
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

    def field(self, name):
        """Get just one field"""

        if self.org is None:
            raise Exception("Organization not set")

        if self.number is None:
            raise Exception("Project number not set")

        # Get the template and build the query
        template = self.jinja.get_template("project/get_field.graphql")
        query = template.render(
            {"orgName": self.org, "projectNumber": self.number, "fieldName": name}
        )
        results = self.run_query(query)

        if results["data"]["organization"]["projectV2"]["field"] is not None:
            return Field(results["data"]["organization"]["projectV2"]["field"])

        return None
