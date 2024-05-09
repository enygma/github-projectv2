from github_projectv2.base import Base
from github_projectv2.item import Item


class Search(Base):
    def issues(self, filter):
        # Get the partial for the issue query
        template = self.jinja.get_template("partial/item.graphql")
        item_query = template.render(
            {"options": {"includeComments": True, "includeTimelineEvents": True}}
        )

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
            item_query,
        )
        print(query)
        results = self.run_query(query)
        print("items: %s" % len(results["data"]["search"]["edges"]))

        # Makes items out of the results
        items = results["data"]["search"]["edges"]
        returnItems = []
        for index in range(len(items)):
            print(index)
            node = items[index]["node"]
            # print("%s\n-------------------\n" % node)
            # print(node.get('timelineItems'))

            item = Item(node)
            returnItems.append(item)

        return returnItems
