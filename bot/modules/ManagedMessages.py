import json
from typing import Dict
from modules.CommonCalls import CommonCalls


class ManagedMessages:

    context_window: Dict[str | int, list] = {}
    managed_messages: Dict[str | int, list] = {}

    async def check_restrictions(message_list: list) -> bool:
        """Internal function for checking if the context window is within 'X' items"""
        if len(message_list) >= int(CommonCalls.config()["maxContext"]):
            message_list.pop(0)  # removes the first element in the list
            return False
        else:
            return True

    async def add_to_message_list(
        channel_id: str | int, message_id: str | int, message: str
    ) -> int:
        """
        Allows addition of an item to the message dictionary, has restraints called by `ManagedMessages.check_restrictions()`
        Returns ID of message appended to list `ManagedMessages.managed_messages`
        """

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

        return message_id

    async def remove_from_message_list(
        channel_id: str | int, message_id: str | int
    ) -> None:
        """Allows removal of an item from the message dictionary from the message id, will also update the message id list and message text list"""

        context_window = ManagedMessages.context_window
        managed_messages = ManagedMessages.managed_messages

        if channel_id in managed_messages and channel_id in context_window:
            try:
                # Filter out all occurrences of message_id in the list
                managed_messages[channel_id] = [
                    msg for msg in managed_messages[channel_id] if msg != message_id
                ]
                context_window[channel_id] = [
                    text for text in context_window[channel_id] if text != message_id
                ]
            except Exception as e:
                print(
                    f"An error occurred while removing message ID {message_id} from channel {channel_id}: {e}"
                )
        else:
            print(f"Channel ID {channel_id} not found.")

    async def remove_message_from_index(channel_id: str | int, index: int):
        """Allows removal of message from list with use of an index"""

        context_window = ManagedMessages.context_window
        managed_messages = ManagedMessages.managed_messages

        try:
            context_window.pop(index)
            managed_messages.pop(index)
        except IndexError:
            return None

    async def remove_channel_from_list(channel_id: str | int):
        """Allows removal of channel ENTIRELY from the current dictionary"""

        context_window = ManagedMessages.context_window
        managed_messages = ManagedMessages.managed_messages

        if channel_id in managed_messages and channel_id in context_window:
            message = (
                CommonCalls.config()["wack_message"]
                or f"Context window cleared! :ok_hand: [Removed {len(context_window[channel_id])}]"
            )

            del managed_messages[channel_id]
            del context_window[channel_id]

            return message

        else:
            return (
                CommonCalls.config()["wack_error"]
                or "No context window found. :pensive:"
            )


class headless_ManagedMessages:
    """This class deals with instances of managed messages without... without something im not sure what"""

    context_window: Dict[str | int, list] = {}
    managed_messages: Dict[str | int, list] = {}

    async def check_restrictions(message_list: list) -> bool:
        """Internal function for checking if the context window is within 'X' items"""
        if len(message_list) >= int(CommonCalls.config()["maxContext"]):
            message_list.pop(0)  # removes the first element in the list
            return False
        else:
            return True

    async def add_to_message_list(channel_id, text, check_restrictions=True):
        """
        Adds messages loosely to the headless message list
        """

        context_window = headless_ManagedMessages.context_window

        if channel_id not in context_window:
            context_window[channel_id] = []

        message_list: list = context_window[channel_id]

        if check_restrictions:
            await headless_ManagedMessages.check_restrictions(message_list)

        # pre apend
        print(
            "[PRE] Add to window function call `add_to_message_list` (Message from line 149 @ modules/ManagedMessages.py)"
        )
        message_list.append(text)  # author : text
        # post append
        print(
            "[POST] Add to window function call `add_to_message_list` (Message from line 152 @ modules/ManagedMessages.py)"
        )
        print(message_list)

    async def remove_message_from_index(channel_id: str | int, index: int):
        """Allows removal of message from list with use of an index"""

        context_window = headless_ManagedMessages.context_window
        managed_messages = headless_ManagedMessages.managed_messages

        try:
            context_window.pop(index)
            managed_messages.pop(index)
        except IndexError:
            return None
