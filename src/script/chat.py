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
        default=GeminiModel.Gemma_3_27b,
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

    commands = {
        "exit": ["/exit", "/quit", "/q"],
        "help": ["/help", "/h"],
        "model": ["/model"],
    }
    print("Initializing CampLLM...", flush=True)

    llm = LLM(model_name=args.model)
    embedder = Embedding()
    database = Database(uri=args.database_uri, embedding_function=embedder)
    rag = RAG(database=database, llm=llm, embedder=embedder)

    print(
        f"Welcome to the CampLLM chatbot! Type {', '.join(commands['exit'])} to end the session."
    )

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in commands["exit"]:
            print("Goodbye!")
            break
        elif user_input.lower() in commands["help"]:
            print(f"Commands:")
            for cmd, aliases in commands.items():
                print(f"  {cmd}: {', '.join(aliases)}")
            continue
        elif user_input.lower() in commands["model"]:
            print(f"CampLLM: Running model {llm.model_name.value}")
            continue

        result = rag.ask(question=user_input, n_results=5)
        print(f"\nCampLLM: {result['answer']}\n")

        sources = result.get("sources", [])
        if sources:
            print("Sources:")
            for source in sources:
                print(
                    "- [Source {source_id}] {park_name} | {section_heading} | {section_url}".format(
                        **source
                    )
                )
            print()


if __name__ == "__main__":
    main()
