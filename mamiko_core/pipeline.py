import os
import json
from .system_scanner import scan_system
from .memory_manager import MemoryManager
from .api_manager import APIManager
from .embedding_manager import EmbeddingManager

WINDOW_SIZE = 16
TOP_K       = 5

class Pipeline:
    def __init__(self, core):
        self.core = core
        cfg_dir = core.config.config_dir

        # 1) Skanujemy system tylko raz (przy starcie)
        scan_system(cfg_dir)

        # 2) Ładujemy pełne fakty z pliku JSON
        facts_path = os.path.join(cfg_dir, "system_facts.json")
        try:
            with open(facts_path, encoding="utf-8") as f:
                self.system_facts = json.load(f)
        except Exception:
            self.system_facts = {
                "os": "", "python": "",
                "pip_packages": [], "pacman_packages": []
            }

        # 3) Tworzymy krótkie summary (counts + 5 przykładów)
        sp = self.system_facts["pip_packages"]
        sc = self.system_facts["pacman_packages"]
        ex_pip    = ", ".join(sp[:5])    if sp else "brak pakietów"
        ex_pacman = ", ".join(sc[:5])    if sc else "brak pakietów"
        self.system_summary = (
            f"OS: {self.system_facts['os']}\n"
            f"Python: {self.system_facts['python']}\n"
            f"pip packages: {len(sp)} (np. {ex_pip})\n"
            f"pacman packages: {len(sc)} (np. {ex_pacman})"
        )

        # 4) Inicjalizujemy referencje do menedżerów
        self.memory    = core.memory    # MemoryManager
        self.embedding = core.embedding # EmbeddingManager
        self.api       = core.api       # APIManager

    def build_context(self, user_input: str) -> list[dict]:
        """
        Buduje listę wiadomości (system → user) do wysłania:
        1) system_summary
        2) opcjonalne system_details, gdy user pyta o pakiety
        3) memory["summary"] i retrieve top-K
        4) ostatnie WINDOW_SIZE wpisów
        5) bieżące pytanie użytkownika
        """
        messages = []

        # a) Krótkie podsumowanie systemowe
        messages.append({
            "role": "system",
            "content": "Fakty o środowisku:\n" + self.system_summary
        })

        # b) Głębokie dane tylko na żądanie
        lc = user_input.lower()
        if any(tok in lc for tok in ["pip", "pakiet", "pacman"]):
            # wstrzykuj pełne JSON-y jako system_details
            full = json.dumps(self.system_facts, indent=2, ensure_ascii=False)
            messages.append({
                "role": "system",
                "content": "Pełne fakty systemowe:\n" + full
            })

        # c) Dodaj historię z memory summary (opcjonalnie)
        mem = self.memory.memory
        if mem.get("summary"):
            messages.append({
                "role": "system",
                "content": "Historyczne podsumowanie:\n" + mem["summary"]
            })

        # d) Retrieve top-K podobnych wiadomości
        query_emb = self.embedding.generate_embedding(user_input)
        top_k_msgs = self.memory.retrieve_top_k(query_emb, k=TOP_K)
        for msg in top_k_msgs:
            messages.append(msg)

        # e) Ostatnie WINDOW_SIZE wiadomości
        window = mem.get("dialogue", [])[-WINDOW_SIZE*2:]  # *2 bo user+assistant
        messages.extend(window)

        # f) Na końcu bieżące pytanie
        messages.append({"role": "user", "content": user_input})

        return messages

    def handle_response(self, user_input: str) -> str:
        # 1) Build and send
        ctx = self.build_context(user_input)
        resp = self.api.generate_response_with_messages(ctx)

        # 2) Zapisz do pamięci
        emb_user   = self.embedding.generate_embedding(user_input)
        emb_assist = self.embedding.generate_embedding(resp)
        self.memory.add_dialogue(user_input, resp, emb_user, emb_assist)

        return resp

