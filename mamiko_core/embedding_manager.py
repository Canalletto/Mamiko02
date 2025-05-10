import math
from .api_manager import APIManager

class EmbeddingManager:
    def __init__(self):
        # Używamy APIManager do pobierania embeddingów z OpenAI
        self.api = APIManager()

    def generate_embedding(self, text: str) -> list[float]:
        """Oblicza embedding tekstu przy użyciu OpenAI Embeddings API."""
        return self.api.generate_embedding(text)

    def cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Oblicza podobieństwo kosinusowe pomiędzy dwoma wektorami."""
        dot = sum(x * y for x, y in zip(vec1, vec2))
        norm_a = math.sqrt(sum(x * x for x in vec1))
        norm_b = math.sqrt(sum(y * y for y in vec2))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

