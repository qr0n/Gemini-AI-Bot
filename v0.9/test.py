async def remove_from_message_list(channel_id: str | int, message_id: str | int, previous: bool = False) -> None:
    """Allows removal of an item from the message dictionary from the message id, will also update the message id list and message text list"""

    context_window = ManagedMessages.context_window
    managed_messages = ManagedMessages.managed_messages

    if channel_id in managed_messages and channel_id in context_window:
        try:
            def remove_message_id_and_previous(lst, message_id, previous):
                indices_to_remove = [i for i, msg in enumerate(lst) if msg == message_id]
                if previous:
                    indices_to_remove = sum(([i-1, i] for i in indices_to_remove if i > 0), [])
                return [msg for i, msg in enumerate(lst) if i not in indices_to_remove]

            # Update both lists by removing message_id and, if specified, their previous elements
            managed_messages[channel_id] = remove_message_id_and_previous(managed_messages[channel_id], message_id, previous)
            context_window[channel_id] = remove_message_id_and_previous(context_window[channel_id], message_id, previous)

            print(f"Message ID {message_id} and previous entries have been removed from channel {channel_id}.")
        except Exception as e:
            print(f"An error occurred while removing message ID {message_id} from channel {channel_id}: {e}")
    else:
        print(f"Channel ID {channel_id} not found.")

# Test Case
x = [0, 1, 2, 3]
def test_do_whatever(lst, message_id: int, previous: bool):
    indices_to_remove = [i for i, msg in enumerate(lst) if msg == message_id]
    if previous:
        indices_to_remove = sum(([i-1, i] for i in indices_to_remove if i > 0), [])
    return [msg for i, msg in enumerate(lst) if i not in indices_to_remove]

# Example
x = test_do_whatever(x, 1, previous=True)
print(x)  # Output: [2, 3]