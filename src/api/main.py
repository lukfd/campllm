from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import os

from src.rag.rag import RAG
from src.database.database import Database
from src.rag.llm import LLM
from src.database.embedding import Embedding

app = FastAPI()
templates = Jinja2Templates(directory="src/api/templates")

# Initialize components
CHROMA_URI = os.environ.get("CHROMA_URI", "http://localhost:8000")
embedding_function = Embedding()
db = Database(uri=CHROMA_URI, embedding_function=embedding_function)
llm = LLM()
rag_system = RAG(database=db, llm=llm, embedder=embedding_function)


class ChatRequest(BaseModel):
    question: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},  # You can add other variables here if needed
    )


@app.post("/api/chat")
async def chat(chat_request: ChatRequest):
    # rag_system.ask() returns a dictionary with 'answer' and 'sources'
    response_data = rag_system.ask(chat_request.question)
    return response_data


def main():
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
