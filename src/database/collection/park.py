from __future__ import annotations


class ParkCollection:
    def __init__(self, client, embedding_function=None):
        self.client = client
        self.embedding_function = embedding_function
        self._collection_name = "parks"

        # Initialize the underlying ChromaDB collection immediately
        self.collection = self.client.get_or_create_collection(
            name=self._collection_name,
            embedding_function=self.embedding_function,
        )

    def query(self, query_text: str, n_results: int = 5):
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas"],
        )

    def __getattr__(self, name):
        return getattr(self.collection, name)
