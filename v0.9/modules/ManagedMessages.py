import json
from typing import Dict

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class ManagedMessages:

    def __init__(self):
        self.context_window: Dict[str | int, list] = {}
        self.managed_messages: Dict[str | int, list] = {}

    def check_restrictions(self, message_list : list):
        if len(message_list) >= config["GEMINI"]["MAX_CONTEXT_WINDOW"]:
            message_list.pop(0) # removes the first element in the list
            return True
        else:
            return False

    def add_to_message_list(self, channel_id: str | int, message_id: str | int, username : str, in_put: str):
        message_list = self.context_window[channel_id]
        managed_message_list = self.managed_messages[channel_id]

        if self.check_restrictions(message_list) and self.check_restrictions(managed_message_list):
            message_list.append(f"{username} : {in_put}")
            managed_message_list.append(message_id)
    
    # TODO Add remove from message list