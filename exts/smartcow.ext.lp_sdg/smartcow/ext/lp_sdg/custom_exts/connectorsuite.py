import omni
import asyncio

import pandas as pd

from elasticsearch import Elasticsearch

###################
## MDX CONNECTOR ##
###################

class MDXConnector():
    """
    A custom connector to fetch and retrieve data from MDX and/or all possible future connectors
    """
    # Get endpoint @ Marion kafka broker/elastic search connector
    def __init__(self, elastic_endpoint=["http://172.20.2.25:9200"]):
        self.elastic_endpoint = elastic_endpoint
    
    # RETRIEVE DATA FROM MDX CLUSTER
    def get_mdx_data(self, elastic_endpoint, elastic_index="mdx-frames-*"):
        print("Fetching ES data... ")

        num_records = 10000
        es = Elasticsearch(elastic_endpoint)

        # Check if the node is even alive
        print(es.ping())
        print(es.cluster.health())

        # Perform basic search on active ES cluster
        res = es.search(
            index=elastic_index, query={"match_all": {}}, size=num_records, filter_path=["hits.hits._source"]
        )

        return res


    def format_mdx_data(self, data):
        print("Formatting ES Data... ")
        data = []
        for doc in data["hits"]["hits"]:
            data.append(doc["_source"])

        result_df = pd.json_normalize(data)
        result_df["@timestamp"] = pd.to_datetime(result_df["@timestamp"])
        return result_df