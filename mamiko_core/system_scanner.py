# mamiko_core/system_scanner.py
import os, json, platform, subprocess, pkg_resources

def scan_system(config_dir: str) -> None:
    """Zapisuje do config/system_facts.json pełne listy pakietów i info o systemie."""
    os_info = platform.platform()
    py_ver  = platform.python_version()

    # pip packages
    try:
        pip_list = [
            f"{dist.project_name}=={dist.version}"
            for dist in pkg_resources.working_set
        ]
    except Exception:
        pip_list = ["<błąd pobierania pip>"]

    # pacman packages (Arch)
    try:
        out = subprocess.check_output(
            ["pacman", "-Q"], stderr=subprocess.DEVNULL, text=True
        )
        sys_list = out.strip().splitlines()
    except Exception:
        sys_list = ["<błąd pobierania pacman>"]

    payload = {
        "os": os_info,
        "python": py_ver,
        "pip_packages": pip_list,
        "pacman_packages": sys_list
    }

    path = os.path.join(config_dir, "system_facts.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
