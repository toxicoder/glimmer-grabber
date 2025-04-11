import json

class ConfigManager:
    def __init__(self, config_file="config.json"):
        with open(config_file, "r") as f:
            self.config = json.load(f)

    def get_input_path(self):
        return self.config.get("input_path")

    def get_output_path(self):
        return self.config.get("output_path")

    def get_threshold(self):
        return self.config.get("threshold")

    def get_api_key(self):
        return self.config.get("api_key")
