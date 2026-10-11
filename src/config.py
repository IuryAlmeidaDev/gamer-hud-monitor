import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "x": 100,
    "y": 100,
    "hotkey": "F9",
    "update_interval_ms": 1000,
    "locked": True,
    "opacity": 0.85,
}

class ConfigManager:
    """Gerencia a persistência de configurações do HUD em formato JSON."""

    def __init__(self, file_path: str = "config.json"):
        self.file_path = Path(file_path)
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """Carrega configurações do disco ou inicializa com valores padrão."""
        if not self.file_path.exists():
            self.config = DEFAULT_CONFIG.copy()
            self.save()
            return self.config
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                self.config = {**DEFAULT_CONFIG, **loaded}
        except Exception:
            self.config = DEFAULT_CONFIG.copy()
        return self.config

    def save(self, data: Dict[str, Any] = None) -> None:
        """Salva as configurações atuais no arquivo JSON."""
        if data is not None:
            self.config.update(data)
        # Garante diretório pai se necessário
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        """Recupera uma configuração por chave."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Define uma configuração por chave."""
        self.config[key] = value
