# Park LLM

Conversational AI final project

## Reranking (recommended)

After first-pass vector retrieval, add a reranking step before sending context to the LLM.

Why:

- Retrieval recall can be good while precision is still noisy.
- Reranking improves which chunks make the final prompt.

Current options in this repo:

- `TokenOverlapReranker` (default, no extra dependencies)
- `CrossEncoderReranker` (higher quality, requires `sentence-transformers`)

Example:

```python
from src.rag.rag import RetrievedChunk, RAGRetriever, TokenOverlapReranker

candidates = [
	RetrievedChunk(id="c1", text="Water is available year-round.", score=0.71),
	RetrievedChunk(id="c2", text="The campground is closed for the season.", score=0.69),
]

retriever = RAGRetriever(reranker=TokenOverlapReranker())
top_chunks = retriever.rerank("is the campground open?", candidates, top_k=1)
```

Then send `top_chunks` text (plus metadata/citations) to the LLM as context.
