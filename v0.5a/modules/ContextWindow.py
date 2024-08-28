import json

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

max_context_window = config["MAX_CONTEXT_WINDOW"]

class ContextWindow:
    context_window: dict = {}