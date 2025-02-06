from github_projectv2.base import Base
from github_projectv2.item import Item


class Search(Base):
    def __init__(self, node=None):
        super().__init__()

        self.first = 10
        self.itemEndCursor = ""
        self.hasNextPage = True

    def issues(self, **kwargs):
        """Get the issues for the search"""

        filter = kwargs.get("filter", "")
        options = {
            "includeComments": True,
            "includeTimelineEvents": True,
            "useSlimIssue": False,
        }
        # If the slim option is passed, set the slim flag to True, otherwise set it to False
        slim = kwargs.get("slim", False)
        if slim:
            options["useSlimIssue"] = True

        # Get the partial for the issue query
        issue_template = (
            "partial/issue_item_slim.graphql"
            if options["useSlimIssue"] == True
            else "partial/issue_item.graphql"
        )
        template = self.jinja.get_template(issue_template)
        item_query = template.render({"options": options})
        start = 50

        query = """{
            search(
                query: "%s"
                type: ISSUE
                first: %s
                after: AFTER
            ) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                edges {
                node {
                    ... on Issue {
                    %s
                    }
                }
                }
            }
        }
        """ % (
            filter,
            start,
            item_query,
        )

        # Replace for our "AFTER" so we can paginate
        query = query.replace(
            "AFTER", '"{}"'.format(self.itemEndCursor) if self.itemEndCursor else "null"
        )
        results = self.run_query(query)

        # Get the page info to see about pagination
        pageInfo = results["data"]["search"]["pageInfo"]
        if pageInfo["hasNextPage"]:
            self.hasNextPage = True
            self.itemEndCursor = pageInfo["endCursor"]
        else:
            self.hasNextPage = False
            self.itemEndCursor = ""

        # Makes items out of the results
        items = results["data"]["search"]["edges"]
        returnItems = []
        for index in range(len(items)):
            node = items[index]["node"]
            item = Item(node)
            returnItems.append(item)

        return returnItems
