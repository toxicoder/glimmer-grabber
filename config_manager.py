import json
from typing import Optional, Any

class ConfigManager:
    def __init__(self, config_file: str = "config.json") -> None:
        with open(config_file, "r") as f:
            self.config = json.load(f)

    def get_input_path(self) -> Optional[str]:
        return self.config.get("input_path")

    def get_output_path(self) -> Optional[str]:
        return self.config.get("output_path")

    def get_threshold(self) -> Optional[float]:
        return self.config.get("threshold")

    def get_api_key(self) -> Optional[str]:
        return self.config.get("api_key")
