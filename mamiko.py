#!/usr/bin/env python3
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.panel import Panel

from mamiko_core import MamikoCore
from plugins.plugin_manager import PluginManager

# Inicjalizacja konsoli i sesji CLI
display_console = Console()
style = Style.from_dict({"prompt": "ansigreen bold"})
session = PromptSession(
    message=HTML('<prompt>DAR&gt; </prompt>'),
    style=style
)

# Tworzymy rdzeń, pipeline i managera wtyczek
mamiko = MamikoCore()
plugins = PluginManager(mamiko.config.get_plugins_dir())

def mamiko_cli():
    """Główna pętla CLI."""
    # Witaj z wyświetlonym powitaniem w kolorze niebieskim
    display_console.print(Panel.fit(
        "Jestem Mamiko02- Witaj!",
        style="bright_cyan"  # Kolor powitania (można zmienić na dowolny)
    ))

    while True:
        try:
            text = session.prompt().strip()
        except (KeyboardInterrupt, EOFError):
            display_console.print("\n[red]Zamykam aplikację.[/red]")
            sys.exit(0)

        if not text:
            continue
        if text.lower() in ["exit", "quit"]:
            display_console.print("[red]Zamykam aplikację.[/red]")
            break

        if text.startswith("!"):
            process_plugin_command(text)
        else:
            response = process_user_input(text)
            # Kolor odpowiedzi - np. "ansigreen" zmienia się na dowolny inny kolor
            display_console.print(
                Panel(response, title="Mamiko", style="bright_yellow")  # Styl odpowiedzi
            )

def process_user_input(user_input: str) -> str:
    """
    Przekazuje zapytanie przez pipeline, który buduje kontekst,
    wysyła embeddingi, retrieve, summary i zapisuje pamięć.
    """
    return mamiko.pipeline.handle_response(user_input)

def process_plugin_command(command: str):
    """Obsługa komend wtyczek (prefiks `!`)."""
    parts = command.split(maxsplit=1)
    plugin_name = parts[0][1:]
    args = parts[1].split() if len(parts) > 1 else []
    try:
        result = plugins.run(plugin_name, *args)
        # Kolor panelu wtyczki - zmień kolor panelu wtyczki
        display_console.print(
            Panel(result, title=f"Wtyczka {plugin_name}", style="bright_green")  # Styl dla wtyczek
        )
    except Exception as e:
        display_console.print(f"[red]Błąd w wtyczce '{plugin_name}': {e}[/red]")

if __name__ == "__main__":
    mamiko_cli()

