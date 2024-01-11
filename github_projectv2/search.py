from github_projectv2.base import Base
from github_projectv2.item import Item


class Search(Base):
    def issues(self, filter):
        # Get the partial for the issue query
        template = self.jinja.get_template("partial/item.graphql")
        itemQuery = template.render({"options": []})

        query = """{
            search(
                query: "%s"
                type: ISSUE
                first: 10
            ) {
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
            itemQuery,
        )
        results = self.run_query(query)

        # Makes items out of the results
        items = results["data"]["search"]["edges"]
        returnItems = []
        for index in range(len(items)):
            node = items[index]["node"]
            item = Item(node)
            returnItems.append(item)

        return returnItems
