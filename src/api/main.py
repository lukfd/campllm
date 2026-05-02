from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.genai.errors import ServerError
from pydantic import BaseModel
import uvicorn
import os
import logging

from src.rag.rag import RAG
from src.database.database import Database
from src.rag.llm import LLM
from src.database.embedding import Embedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="src/api/templates")
app.mount("/static", StaticFiles(directory="src/api/templates"), name="static")

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
    try:
        # rag_system.ask() returns a dictionary with 'answer' and 'sources'
        response_data = rag_system.ask(chat_request.question)
        return response_data
    except ServerError as e:
        logger.error(f"GenAI ServerError while handling chat request: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unhandled error while handling chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/model")
async def get_model():
    return {"model": llm.model_name.value}


def main():
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
