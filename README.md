# Park LLM

Conversational AI final project

## Environment Variables

The application can be configured using the following environment variables:

- `CHROMA_URI`: The full URI for the ChromaDB instance. Defaults to `http://chroma:8000` for scripts and is set in `docker-compose.yaml` for the API.
- `CHROMA_PASSWORD`: The authentication token for ChromaDB.
- `GOOGLE_API_KEY`: Your API key for Google Gemini.

## Lucaone

On `lucaone` the Chroma container is not port-mapped to the host. Use the container IP for `CHROMA_URI` when running scripts on that machine, for example:

```
CHROMA_URI=http://172.19.0.15:8000
```

Also set the Chroma token in the environment (or your local `.env`) as:

```
CHROMA_PASSWORD=your-password
CHROMA_URI=http://172.19.0.15:8000
```

To run the collection script, after having setup the environment variables, run

```bash
uv run park --chrome-path $(which google-chrome) --collect --park-file ./parks.jsonl
```

## Data Collection

The indexing workflow can optionally collect fresh raw park data with the Node crawler.

- Script: `src/script/collect.js`
- Triggered by: `uv run index --collect --park-file <path>`

The index script writes raw data to the provided park file path, then runs cleaning and indexing.

## Database

The database script is a utility CLI for validating and inspecting the ChromaDB index.

- Script: `src/script/database.py`
- Command: `uv run database [--database-uri <uri>] [--list] [--query "..."] [--peek]`

What it does:

1. Creates a `Database` instance backed by Chroma HTTP client.
2. Exposes the parks collection through `database.parks`.
3. Supports:
	- `--list`: list available collections
	- `--query`: semantic query against the parks collection
	- `--peek`: inspect a sample of stored entries

## Chat

The chat script is the interactive RAG interface.

- Script: `src/script/chat.py`
- Command: `uv run chat [--model <GeminiModel>] [--database-uri <uri>] [--info]`

What it does:

1. Initializes `LLM`, `Embedding`, `Database`, and `RAG`.
2. Reads user input in a loop.
3. Runs `rag.ask(question, n_results=5)` for each message.
4. Prints:
	- model answer
	- sources (park name, section heading, URL)

Commands:

- Exit: `/exit`, `/quit`, `/q`
- Help: `/help`, `/h`

Logging:

- Default logging is `WARNING`.
- Pass `--info` to enable RAG retrieval info logs.

## Script Architecture

### Index Script

- Script: `src/script/index.py`
- Command: `uv run index --park-file <path> [--collect] [--database-uri <uri>] [--debug]`

Flow:

1. Optionally collects raw data with the Node crawler (`--collect`).
2. Cleans the input file with `Cleaner`.
3. Creates `Database` and uses `database.parks`.
4. Runs `Indexer` to chunk, embed, and upsert park data into ChromaDB.

### Database Script

- Script: `src/script/database.py`

Flow:

1. Connects to ChromaDB via `Database`.
2. Uses `database.parks` for collection operations.
3. Provides quick list/query/peek commands for verification and debugging.

### Chat Script

- Script: `src/script/chat.py`

Flow:

1. Builds application dependencies (`LLM`, `Embedding`, `Database`, `RAG`).
2. Receives user questions.
3. `RAG` retrieves top documents from ChromaDB and builds grounded context with source IDs.
4. `LLM` generates an answer from that context.
5. Chat prints answer and source references.

### RAG Source Handling

`RAG.ask()` returns:

- `answer`: generated response text
- `sources`: source metadata (optionally filtered by cited source IDs)
- `cited_source_ids`: IDs parsed from `[Source N]` citations in the answer


