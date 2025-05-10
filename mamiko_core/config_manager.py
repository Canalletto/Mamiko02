#!/usr/bin/env python3
import os
import json

class ConfigManager:
    def __init__(self, base_dir=None):
        # Jeżeli podano base_dir, użyj go; w przeciwnym razie to root projektu (folder zawierający config/)
        if base_dir:
            self.base_dir = os.path.expanduser(base_dir)
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            self.base_dir = project_root

        # Katalogi
        self.config_dir  = os.path.join(self.base_dir, "config")
        self.plugins_dir = os.path.join(self.base_dir, "plugins")

        # Pliki w config_dir
        self.api_key_file      = os.path.join(self.config_dir, "api_key.json")
        self.memory_file       = os.path.join(self.config_dir, "memory.json")
        self.file_memory_file  = os.path.join(self.config_dir, "file_memory.json")

        os.makedirs(self.config_dir, exist_ok=True)

        # Jeśli nie ma klucza, zostawiamy szablon
  

    def load_api_key(self) -> str:
        try:
            with open(self.api_key_file, encoding="utf-8") as f:
                data = json.load(f)
            return data.get("openai_api_key") or data.get("api_key")
        except Exception as e:
            raise FileNotFoundError(f"Nie można wczytać klucza API z {self.api_key_file}: {e}")

    def get_memory_file(self) -> str:
        return self.memory_file

    def get_plugins_dir(self) -> str:
        return self.plugins_dir

