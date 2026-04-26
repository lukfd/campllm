import os
from typing import Dict

from chromadb import EmbeddingFunction
from chromadb.utils.embedding_functions import register_embedding_function
from model2vec import StaticModel

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")


@register_embedding_function
class Embedding(EmbeddingFunction):
    def __init__(self, model_name: str = "minishlab/potion-base-8M"):
        self.model_name = model_name
        self.model = StaticModel.from_pretrained(self.model_name)

    def embed(self, text: str) -> list[float]:
        vector = self.model.encode([text])[0]
        return vector.tolist() if hasattr(vector, "tolist") else list(vector)

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts)

        if hasattr(vectors, "tolist"):
            return vectors.tolist()

        return [
            vector.tolist() if hasattr(vector, "tolist") else list(vector)
            for vector in vectors
        ]

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self.embed_many(list(input))

    @staticmethod
    def name() -> str:
        return "model2vec-embedding"

    def get_config(self) -> Dict[str, str]:
        return {"model_name": self.model_name}

    @staticmethod
    def build_from_config(config: Dict[str, str]) -> "EmbeddingFunction":
        return Embedding(model_name=config["model_name"])
