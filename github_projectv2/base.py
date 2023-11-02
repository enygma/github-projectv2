import os

import requests
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

load_dotenv()
headers = {"Authorization": "bearer %s" % os.getenv("GITHUB_API_TOKEN")}


class Base:
    def __init__(self, request=None):
        self.request = None

        # Set up the Jinja2 environment
        dirname = os.path.dirname(__file__)
        self.jinja = env = Environment(
            loader=FileSystemLoader("%s/queries" % dirname),
            autoescape=select_autoescape(),
        )

    def run_query(self, query: str, data={}):
        """
        Takes in a GraphQL query and optional data and returns the results.
        """
        request = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": data},
            headers=headers,
        )
        if request.status_code == 200:
            # print("OUT: %s" % request.text)
            return request.json()
        else:
            raise Exception(
                "Query failed to run by returning code of {}. {}".format(
                    request.status_code, query
                )
            )

    def get_query(self, name: str):
        """
        Takes in a query name and returns the contents of the file in the
        queries directory with that name.
        """
        dirname = os.path.dirname(__file__)
        path = "%s/queries/%s.graphql" % (dirname, name)

        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        else:
            raise Exception("Query %s does not exist." % name)

    def convert_quotes(self, dict):
        """
        Takes in a set of key/value pairs and converts the values to strings
        with double-quotes to work correctly in GraphQL queries.
        """
        results = []
        for item in dict:
            results.append('"%s"' % item)
        results = ",".join(results)
        results = "[%s]" % results

        return results
