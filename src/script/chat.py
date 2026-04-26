import argparse
import logging

from src.database.embedding import Embedding
from src.rag.llm import LLM, GeminiModel
from src.database.database import Database
from src.rag.rag import RAG


def main():
    parser = argparse.ArgumentParser(description="Chatbot interface for CampLLM.")
    parser.add_argument(
        "--model",
        type=GeminiModel,
        help="Gemini model to use for the chatbot",
        default=GeminiModel.Gemini_2_5_flash_lite,
    )
    parser.add_argument(
        "--database-uri",
        type=str,
        help="Database URI for retrieving park information",
        default="http://localhost:8000",
    )
    parser.add_argument("--info", action="store_true", help="Enable RAG info logs")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    if args.info:
        logging.getLogger("src.rag.rag").setLevel(logging.INFO)

    exit_commands = ["/exit", "/quit", "/q"]
    print("Initializing CampLLM...", flush=True)

    llm = LLM(model_name=args.model)
    embedder = Embedding()
    database = Database(uri=args.database_uri, embedding_function=embedder)
    rag = RAG(database=database, llm=llm, embedder=embedder)

    print(
        f"Welcome to the CampLLM chatbot! Type {', '.join(exit_commands)} to end the session."
    )

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in exit_commands:
            print("Goodbye!")
            break

        prompt = rag.generate_prompt(question=user_input, n_results=5)

        llm_response = llm.send_message(prompt)
        print(f"CampLLM: {llm_response}")


if __name__ == "__main__":
    main()
