from elasticsearch import Elasticsearch
import uuid

class ElasticSearchFactory(object):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def create(self) -> Elasticsearch:
        return Elasticsearch(
            [{'host': self.host, 'port': self.port}]
        )

class ElasticSearchIndex(object):
    def __init__(
            self,
            elastic_factory: ElasticSearchFactory,
            index_name: str,
            doc_type: str,
            index_mapper: dict):

        self.index_name = index_name
        self.index_mapper = index_mapper
        self.doc_type = doc_type
        self.elastic_factory = elastic_factory
        self.instance = None

    def connection(self) -> Elasticsearch:
        """Connect to an ElasticSearch server + Map a new index

            Returns:
            instance (Elasticsearch): Instance to ElasticSearch Connection
        """
        if not self.instance:
            self.instance = self.elastic_factory.create()

            if not self.instance.indices.exists(self.index_name):
                self.instance.indices.create(
                    index=self.index_name,
                    body=self.index_mapper
                )

        return self.instance

    def index(self, doc_id: str ,body: dict) -> bool:
        """Insert/Update a document to an ElasticSearch server

        Parameters:
        doc_id (str): Document ID
        body (dict): Document data

        Returns:
        (ElasticsearchIndex): Index Reference
        """
        return self.connection().index(
            index=self.index_name,
            id=doc_id,
            body=body
        )

    def get_hotel_document(self, hotel_name: str) -> dict:
        """query a document by hotel name.

        Parameters:
        hotel_name (str): Hotel Name

        Returns:
        (list): Query Reusults
        """
        return self.connection().search(index=self.index_name,
                        body={"query": {"match": { 'name':hotel_name}}}
                    )