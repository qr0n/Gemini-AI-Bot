import json
from typing import Dict

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

max_context_window = config["GEMINI"]["MAX_CONTEXT_WINDOW"]

class ContextWindow:
    context_window: Dict[str | int, list] = {}