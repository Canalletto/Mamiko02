import os
import importlib.util

class PluginManager:
    def __init__(self, plugins_dir="~/mamiko/plugins"):
        self.plugins_dir = os.path.expanduser(plugins_dir)
        self.plugins = {}
        self.load_plugins()

    def load_plugins(self):
        """Wczytuje wszystkie wtyczki z katalogu plugins/."""
        if not os.path.isdir(self.plugins_dir):
            os.makedirs(self.plugins_dir, exist_ok=True)
            return
        
        for fname in os.listdir(self.plugins_dir):
            if fname.endswith(".py"):
                plugin_name = fname[:-3]  # Nazwa pliku bez rozszerzenia
                plugin_path = os.path.join(self.plugins_dir, fname)
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "run"):
                    self.plugins[plugin_name] = module
                else:
                    print(f"[PluginManager] Wtyczka {plugin_name} nie posiada funkcji 'run'.")

    def list_plugins(self):
        """Zwraca listę dostępnych wtyczek."""
        return list(self.plugins.keys())

    def run_plugin(self, plugin_name, *args, **kwargs):
        """Uruchamia wtyczkę o podanej nazwie."""
        if plugin_name in self.plugins:
            try:
                return self.plugins[plugin_name].run(*args, **kwargs)
            except Exception as e:
                return f"[PluginManager] Błąd w wtyczce {plugin_name}: {e}"
        else:
            return f"[PluginManager] Wtyczka {plugin_name} nie znaleziona."

