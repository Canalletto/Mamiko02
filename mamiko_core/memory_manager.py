import os
import json
import math

class MemoryManager:
    def __init__(self, config_dir):
        self.memory_file       = os.path.join(config_dir, "memory.json")
        self.file_memory_file  = os.path.join(config_dir, "file_memory.json")
        self.HIERARCHY_THRESHOLD = 50
        self.BLOCK_SIZE         = 10

        self.memory      = self.load_memory()
        self.file_memory = self.load_file_memory()

    def load_memory(self):
        """Wczytuje pamięć; jeśli plik nie istnieje lub jest pusty/uszkodzony, zwraca domyślną strukturę."""
        default = {
            "facts": {"installed_packages": [], "preferences": {}},
            "summary": "",
            "dialogue": [],
            "dialogue_embeddings": []
        }
        if not os.path.exists(self.memory_file):
            return default
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            # plik pusty/uszkodzony -> przywracamy domyślną pamięć
            self.memory = default
            self.save_memory()
            return default

    def save_memory(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2)

    def load_file_memory(self):
        """Wczytuje pamięć plików; podobnie przywraca domyślne jeśli plik jest nieprawidłowy."""
        default = {"tracked_files": {}}
        if not os.path.exists(self.file_memory_file):
            return default
        try:
            with open(self.file_memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            # przywracamy domyślną pamięć plików
            with open(self.file_memory_file, "w", encoding="utf-8") as fw:
                json.dump(default, fw, indent=2)
            return default

    def add_to_memory(self, user_message, assistant_reply, embedding_user, embedding_assistant):
        """Dodaje parę wiadomość-odpowiedź wraz z embeddingami, zapisuje i podsumowuje."""
        self.memory["dialogue"].append({"role": "user",      "content": user_message})
        self.memory["dialogue_embeddings"].append(embedding_user)
        self.memory["dialogue"].append({"role": "assistant", "content": assistant_reply})
        self.memory["dialogue_embeddings"].append(embedding_assistant)

        self.save_memory()
        self.hierarchical_summarize()

    def hierarchical_summarize(self):
        """Tworzy podsumowania historyczne, gdy dialog przekroczy próg."""
        if len(self.memory["dialogue"]) <= self.HIERARCHY_THRESHOLD:
            return

        old = self.memory["dialogue"][:-self.HIERARCHY_THRESHOLD]
        blocks = [old[i:i + self.BLOCK_SIZE] for i in range(0, len(old), self.BLOCK_SIZE)]
        summaries = []
        for block in blocks:
            text = "\n".join(f"{m['role']}: {m['content']}" for m in block)
            summaries.append(f"Podsumowanie: {text[:100]}...")

        self.memory["summary"] += "\n" + "\n".join(summaries)
        self.memory["dialogue"]            = self.memory["dialogue"][-self.HIERARCHY_THRESHOLD:]
        self.memory["dialogue_embeddings"] = self.memory["dialogue_embeddings"][-self.HIERARCHY_THRESHOLD:]
        self.save_memory()

    def _cosine(self, a: list[float], b: list[float]) -> float:
        """Pomocnicza funkcja do obliczania cosinusowej miary podobieństwa."""
        dot = sum(x*y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x*x for x in a))
        norm_b = math.sqrt(sum(y*y for y in b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

        
    def retrieve_top_k(self, query_embedding: list[float], k: int = 5) -> list[dict]:
        """
        Zwraca listę top-k wiadomości (z całego dialogu) najbardziej
        podobnych do query_embedding. Każdy element to dict {'role':…, 'content':…}.
        """
        sims = []
        for emb, msg in zip(self.memory["dialogue_embeddings"], self.memory["dialogue"]):
            score = self._cosine(query_embedding, emb)
            sims.append((score, msg))
        sims.sort(key=lambda x: x[0], reverse=True)
        # zwróć same wiadomości (bez scores)
        return [msg for score, msg in sims[:k]]


    # alias, którego używa Pipeline:
    def add_dialogue(self, user_message, assistant_reply, embedding_user, embedding_assistant):
        return self.add_to_memory(user_message, assistant_reply, embedding_user, embedding_assistant)

