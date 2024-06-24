from github_projectv2.base import Base
from github_projectv2.item import Item


class Search(Base):
    def __init__(self, node=None):
        super().__init__()

        self.first = 10
        self.itemEndCursor = ""
        self.hasNextPage = False

    def issues(self, filter):
        # Get the partial for the issue query
        template = self.jinja.get_template("partial/item.graphql")
        item_query = template.render(
            {"options": {"includeComments": True, "includeTimelineEvents": True}}
        )
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
