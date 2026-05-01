import chromadb
from urllib.parse import urlparse
from typing import Any
import os

from src.database.embedding import Embedding
from src.database.collection.park import ParkCollection


class Database:
    def __init__(self, uri: str, embedding_function: Embedding | None = None):
        self.uri = uri
        self.embedding_function = embedding_function or Embedding()

        self.parsed = urlparse(uri)
        if not self.parsed.hostname or not self.parsed.port:
            raise ValueError(
                "URI must include host and port, for example: http://localhost:8000"
            )

        headers = {}
        auth_token = os.getenv("CHROMA_PASSWORD")
        if auth_token:
            auth_header = os.getenv(
                "CHROMA_AUTH_TOKEN_TRANSPORT_HEADER", "Authorization"
            )
            headers[auth_header] = f"Bearer {auth_token}"

        self.client = chromadb.HttpClient(
            host=self.parsed.hostname,
            port=self.parsed.port,
            ssl=False,
            headers=headers,
        )

        self.parks = ParkCollection(
            client=self.client, embedding_function=self.embedding_function
        )

    def get_embedding_function(self):
        return self.embedding_function

    def list_collections(self):
        return self.client.list_collections()
