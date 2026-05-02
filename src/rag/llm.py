from enum import Enum
from google import genai
from google.genai import types
from dotenv import load_dotenv


class GeminiModel(Enum):
    # https://ai.google.dev/gemini-api/docs/models
    # List: curl https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY
    Gemini_2_5_flash_lite = "gemini-2.5-flash-lite"
    Gemini_2_5_flash = "gemini-2.5-flash"
    Gemini_3_flash_preview = "gemini-3-flash-preview"
    Gemma_3_27b = "gemma-3-27b-it"
    Gemma_4_31b = "gemma-4-31b-it"


class LLM(genai.Client):
    def __init__(
        self, model_name: GeminiModel = GeminiModel.Gemma_4_31b, **kwargs
    ):
        self.model_name = model_name
        load_dotenv()  # Load environment variables from .env file
        super().__init__(**kwargs)
        self.chat = None

        self.config = types.GenerateContentConfig(
            system_instruction="You are a helpful assistant for answering questions about parks based on the provided information.",
            temperature=0.1,
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        )

    def generate(self, content: str, **kwargs) -> str:
        response = self.models.generate_content(
            model=self.model_name.value,
            contents=content,
            config=self.config,
            **kwargs,
        )
        return response.text

    def start_chat(self, **kwargs):
        self.chat = self.chats.create(model=self.model_name.value, **kwargs)
        return self.chat

    def send_message(self, message: str, **kwargs) -> str:
        if self.chat is None:
            self.start_chat()
        response = self.chat.send_message(message, **kwargs)
        return response.text or ""

    def get_history(self):
        if self.chat is None:
            return []
        return list(self.chat.get_history())

    def clear_chat(self):
        self.chat = None
