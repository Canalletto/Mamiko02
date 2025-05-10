# mamiko_core/__init__.py

from .memory_manager import MemoryManager
from .api_manager import APIManager
from .embedding_manager import EmbeddingManager
from .config_manager import ConfigManager
from .pipeline import Pipeline

class MamikoCore:
    def __init__(self, base_dir=None):
        # Konfiguracja (config_dir → ~/mamiko/config)
        self.config = ConfigManager(base_dir)
        # Pamięć (~/mamiko/config/memory.json)
        self.memory = MemoryManager(self.config.config_dir)
        # Embeddingi
        self.embedding = EmbeddingManager()
        # API (wczyta klucz z ConfigManager)
        self.api = APIManager(core=self)
        # Pipeline, który łączy wszystkie kroki: retrieve, summary, context window, zapis
        self.pipeline = Pipeline(self)

