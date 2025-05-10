#!/usr/bin/env python3
import openai
from openai import BadRequestError
from .config_manager import ConfigManager

class APIManager:
    def __init__(self, core=None, model: str = "gpt-4.1-mini", temperature: float = 0.7):
        """
        core: instancja MamikoCore, by mieć dostęp do config i memory
        """
        self.model = model
        self.temperature = temperature
        self.core = core
        # Ustaw klucz API i system prompt
        if core:
            openai.api_key = core.config.load_api_key()
            self.system_prompt = getattr(core.config, "load_system_prompt", lambda: "")() or ""
        else:
            cfg = ConfigManager()
            openai.api_key = cfg.load_api_key()
            self.system_prompt = getattr(cfg, "load_system_prompt", lambda: "")() or ""

    def generate_response(self, user_input: str) -> str:
        """
        Zwraca odpowiedź, buduje minimalny prompt z system_prompt + user_input
        """
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": user_input})
        return self.generate_response_with_messages(messages)

    def generate_response_with_messages(self, messages: list[dict]) -> str:
        """
        Wysyła listę wiadomości do ChatCompletion i zwraca content.
        """
        try:
            resp = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )
            return resp.choices[0].message.content

        except BadRequestError as e:
            raise RuntimeError(f"BadRequestError: {e}") from e

        except Exception as e:
            raise RuntimeError(f"Błąd OpenAI API: {e}") from e

    def generate_embedding(self, text: str) -> list[float]:
        """Oblicza embedding dla tekstu."""
        try:
            resp = openai.embeddings.create(
                model="text-embedding-3-small",
                input=[text]
            )
            return resp.data[0].embedding

        except Exception as e:
            raise RuntimeError(f"Błąd embeddingu: {e}") from e

