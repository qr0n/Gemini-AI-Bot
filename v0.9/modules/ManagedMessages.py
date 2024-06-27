import json
from typing import Dict

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class ManagedMessages:

    context_window: Dict[str | int, list] = {}
    managed_messages: Dict[str | int, list] = {}

    async def check_restrictions(message_list: list) -> bool:
        """Internal function for checking if the context window is within 'X' items"""
        if len(message_list) >= config["GEMINI"]["MAX_CONTEXT_WINDOW"]:
            message_list.pop(0)  # removes the first element in the list
            return False
        else:
            return True

    async def add_to_message_list(channel_id: str | int, message_id: str | int, message: str) -> None:
        """Allows addition of an item to the message dictionary, has restraints called by `ManagedMessages.check_restrictions()`"""
        
        context_window = ManagedMessages.context_window
        managed_messages = ManagedMessages.managed_messages

        if channel_id not in context_window:
            context_window[channel_id] = []
        if channel_id not in managed_messages:
            managed_messages[channel_id] = []

        message_list = context_window[channel_id]
        managed_message_list = managed_messages[channel_id]

        await ManagedMessages.check_restrictions(message_list)
        await ManagedMessages.check_restrictions(managed_message_list)

        message_list.append(message)
        managed_message_list.append(message_id)

    async def remove_from_message_list(channel_id: str | int, message_id: str | int) -> None:
        """Allows removal of an item from the message dictionary from the message id, will also update the message id list and message text list"""
        
        context_window = ManagedMessages.context_window
        managed_messages = ManagedMessages.managed_messages
        
        if channel_id in managed_messages and channel_id in context_window:
            try:
                index = managed_messages[channel_id].index(message_id)
                managed_messages[channel_id].pop(index)
                context_window[channel_id].pop(index)
            except ValueError:
                print(f"Message ID {message_id} not found in channel {channel_id}.")
        else:
            print(f"Channel ID {channel_id} not found.")

    async def remove_message_from_index(channel_id : str | int, index : int):
        """Allows removal of message from list with use of an index"""
        
        context_window = ManagedMessages.context_window
        managed_messages = ManagedMessages.managed_messages

        try:
            context_window.pop(index)
            managed_messages.pop(index)
        except IndexError:
            return None
    
    async def remove_channel_from_list(channel_id : str | int):
        """Allows removal of channel ENTIRELY from the current dictionary"""
        
        context_window = ManagedMessages.context_window
        managed_messages = ManagedMessages.managed_messages

        if channel_id in managed_messages and channel_id in context_window:
            message = config["MESSAGES"]["wack"] or f"Context window cleared! :ok_hand: [Removed {len(context_window[channel_id])}]"

            del managed_messages[channel_id]
            del context_window[channel_id]
            
            return message
        
        else:
            return config["MESSAGES"]["wack_error"] or "No context window found. :pensive:"